from dataclasses import dataclass
from typing import List, Callable
import requests
from enum import Enum


def getGA(ip: str) -> str:
	resp = requests.get(ip + "/cmd?GA")
	return resp.text


class Season(Enum):
	SUMMER = 1
	WINTER = 0


def to_bool(val: str | None) -> bool | None:
	match val:
		case None, '':
			return None
		case '0':
			return False
		case '1':
			return True
		case _:
			raise Exception('Unknown boolean value: ' + val)


@dataclass
class GaData:
	raw_list: List[str]
	version: float

	def __is_gen1(self) -> bool:
		return self.version < 0.2

	def __is_gen2(self) -> bool:
		return 0.2 <= self.version < 0.3

	def __is_gen3(self) -> bool:
		return self.version >= 0.3

	def power_on(self) -> bool:
		return to_bool(self.raw_list[0])

	def flow(self) -> int:
		return int(self.raw_list[1])

	def target_temperature(self) -> int:
		return int(self.raw_list[2])

	def current_indoors_temperature(self) -> float:
		return float(self.raw_list[32]) / 10

	def current_indoors_humidity(self) -> float:
		return int(self.raw_list[33]) / 10

	def input_fan_speed(self) -> int | None:
		if self.__is_gen1():
			return None
		else:
			return int(self.raw_list[3])

	def output_fan_speed(self) -> int | None:
		if self.__is_gen1():
			return None
		else:
			return int(self.raw_list[4])

	def boost_flow(self) -> int | None:
		if self.__is_gen1():
			return None
		else:
			return int(self.raw_list[6])

	def boost_time(self) -> int | None:
		if self.__is_gen1():
			return None
		else:
			return int(self.raw_list[7])

	def boost_enabled(self) -> bool | None:
		if self.__is_gen1():
			return None
		else:
			return to_bool(self.raw_list[26])

	def filter_class_3_total_hours(self) -> int:
		if self.__is_gen1():
			return int(self.raw_list[6])
		elif self.__is_gen2():
			return int(self.raw_list[11])
		else:
			return int(self.raw_list[12])

	def filter_class_5_total_hours(self) -> int:
		if self.__is_gen1():
			return int(self.raw_list[7])
		elif self.__is_gen2():
			return int(self.raw_list[12])
		else:
			return int(self.raw_list[13])

	def filter_class_7_total_hours(self) -> int:
		if self.__is_gen1():
			return int(self.raw_list[8])
		elif self.__is_gen2():
			return int(self.raw_list[13])
		else:
			return int(self.raw_list[14])

	def current_input_filter_type(self) -> int:
		if self.__is_gen1():
			return int(self.raw_list[9])
		elif self.__is_gen2():
			return int(self.raw_list[14])
		else:
			return int(self.raw_list[15])

	def current_output_filter_type(self) -> int:
		if self.__is_gen1():
			return int(self.raw_list[10])
		elif self.__is_gen2():
			return int(self.raw_list[15])
		else:
			return int(self.raw_list[16])

	def input_filter_hours_used(self) -> int:
		if self.__is_gen1():
			return int(self.raw_list[16])
		elif self.__is_gen2():
			return int(self.raw_list[29])
		else:
			return int(self.raw_list[34])

	def output_filter_hours_used(self) -> int:
		if self.__is_gen1():
			return int(self.raw_list[17])
		elif self.__is_gen2():
			return int(self.raw_list[30])
		else:
			return int(self.raw_list[35])

	def __str__(self):
		return "\n".join(attr + ": " + str(getattr(self, attr)())
		                 for attr in dir(self) if not attr.startswith("_") and callable(getattr(self, attr)))


def parse_ga(dataStr: str) -> GaData:
	dataStr = dataStr.replace("\n", ",")
	rawList = dataStr.split(",")
	return GaData(raw_list=rawList, version=0.3)


mapping = {
	0: "power_on",
	1: "flow",
	2: "targetTemperature",
	3: "(balancing) input fan speed",
	4: "(balancing) output fan speed",
	5: "unknown1boostRelated",
	6: "boostFlow",
	7: "boostTime",
	8: "unknown8",
	9: "(service) toDiff",
	10: "(service) efficiency",
	11: "(service) defrostTime",
	12: "filterClass3Hours",
	13: "filterClass5Hours",
	14: "filterClass7Hours",
	15: "esamonoFiltroTipasInp",
	16: "esamonoFiltroTipasSal",
	17: "(service) drCrit",
	18: "(service) eafLevel",
	19: "(service) ceTime",
	20: "(service) ceInterval",
	21: "(service) dceEafDiff",
	22: "(service) dceInterval",
	23: "?",
	24: "defrostFlag",
	25: "frostFlag1",
	26: "boostEnabled",
	27: "season or state(?)",
	28: "?",
	29: "unknown3BypassRelated",
	30: "?",
	31: "?",
	32: "currentTemperature",
	33: "currentHumidity",
	34: "supplyFilterHoursUsed",
	35: "exhaustFilterHoursUsed",
	36: "unknown4VersionRelated",
	37: "calendarEnabled",
}

# ga = getGA("http://192.168.1.6")
# print("GA: \n" + ga)
#
# # ga = """1,61,21,100,100,1,100,1,30,50,65,60,4464,2976,1488,0,0,50,100,2,120,10,15
# # 0,0,0,0,1,0,0,0,0
# # 245,383,1231,1231,130
# # 0"""
#
# parsed = parse_ga(ga)
#
# print("Parsed by index:")
# [print(str(ix) + ": " + val + " (" + mapping[ix] + ")") for (ix, val) in enumerate(parsed.raw_list)]
#
# #print("Class dir:\n" + str(dir(parsed)))
#
# print("\n\nParsed: \n" + str(parsed))
