import csv
import datetime

from pylena import elements

rank_keys = ["ctc", "cvc", "awc"]

class LenaFile:
    def __init__(self, lena_file=""):
        self.range = []

        if lena_file:
            with open(lena_file, "rU") as input:
                reader = csv.reader(input)
                reader.next()
                for index, row in enumerate(reader):
                    data_type = row[0]
                    child_key = row[1]
                    id = row[2]
                    last_name = row[3]
                    first_name = row[4]
                    birth_date = row[5]
                    age = row[6]
                    sex = row[7]
                    dlp = row[8]
                    processing_file = row[9]
                    timestamp = row[10]
                    duration = row[11]
                    meaningful = row[12]
                    distant = row[13]
                    tv = row[14]
                    tv_percent = int(row[15].replace("%", ""))
                    noise = row[16]
                    silence = row[17]
                    awc_actual = int(row[18])
                    ctc_actual = int(row[21])
                    cvc_actual = int(row[24])
                    ava_stdscore = float(row[27])
                    ava_stdscore_percent = int(row[28].replace("%", ""))

                    lena_row = elements.LenaRow(data_type=data_type, child_key=child_key, id=id,
                                                last_name=last_name, first_name=first_name,
                                                birth_date=birth_date, age=age, sex=sex,
                                                dlp=dlp, processing_file=processing_file,
                                                timestamp=timestamp, duration=duration,
                                                meaningful=meaningful, distant=distant,
                                                tv=tv, tv_percent=tv_percent, noise=noise,
                                                silence=silence, awc_actual=awc_actual,
                                                ctc_actual=ctc_actual, cvc_actual=cvc_actual,
                                                ava_stdscore=ava_stdscore, row_index=index,
                                                ava_stdscore_percent=ava_stdscore_percent)

                    self.range.append(lena_row)

            child_keys = [element.child_key for element in self.range]
            child_key_set = set(child_keys)
            if len(child_key_set) == 1:
                self.child_key = child_key_set.pop()

            sexes = [element.sex for element in self.range]
            sex_set = set(sexes)
            if len(sex_set) == 1:
                self.sex = sex_set.pop()

            birthdates = [element.birth_date for element in self.range]
            birth_set = set(birthdates)
            if len(birth_set) == 1:
                self.birth_date = birth_set.pop()

            ages = [element.age for element in self.range]
            age_set = set(ages)
            if len(age_set) == 1:
                self.age = age_set.pop()

    def get_range(self, begin=0, end=0):
        if end > len(self.range)-1 or begin > len(self.range)-1:
            raise IndexError("begin={}  end={} were outside the range. Max index is {}".format(begin, end, len(self.range)))
        else:
            row_range = self.range[begin:end]
            lena_range = elements.LenaRange(row_range)
            return lena_range

    def get_rows(self, rows):
        """
        :param rows: a list of indices e.g. [1, 44, 65, 87, 9]
        :return: a list of LenaRow corresponding to those indices
        """
        if not rows:
            raise ValueError("you need to privide a list of indices to retrieve those rows")
        else:
            results = []
            for index in rows:
                if len(self.range)-1 < index:
                    raise IndexError("the index: {}   is out of bounds. Max index is {}".format(index, len(self.range)))
                else:
                    results.append(self.range[index])
        return results


    def rank_window(self, window_size, *keys):
        keys = [key.lower() for key in keys]
        for key in keys:
            if key not in rank_keys:
                raise ValueError("key: {}   not a valid ranking key".format(key))

        start = 0
        end = window_size

        region_values = []

        window = self.get_range(start, end)

        while end <= len(self.range)-1:
            range_sum = window.sum(*keys)
            range_avg = float(range_sum) / window_size
            region_values.append((start, range_avg))

            start += 1
            end += 1

            if end <= len(self.range)-1:
                window = self.get_range(start, end)

        ranked_regions = sorted(region_values,
                                key=lambda region: region[1],
                                reverse=True)
        return ranked_regions

    def top_rows(self, n=5, *keys):
        keys = [key.lower() for key in keys]
        for key in keys:
            if key not in rank_keys:
                raise ValueError("key: {}   not a valid ranking key".format(key))

        ranked = self.rank_window(1, *keys)

        return ranked[:n]

    def total_time(self, begin=0, end=None):
        if end > len(self.range) or begin > len(self.range)-1:
            raise IndexError("begin={}  end={}  were outside the range. Max index is {}"
                             .format(begin, end, len(self.range)))
        else:
            total_time = datetime.timedelta()
            if not begin and not end:
                begin = 0
                end = len(self.range)
            for row in self.range[begin:end]:
                split_dur = map(int, row.duration.split(":"))
                total_time += datetime.timedelta(hours=split_dur[0], minutes=split_dur[1], seconds=split_dur[2])

            return total_time

    def sum(self, *keys):
        sum = 0
        for element in self.range:
            if "ctc" in keys:
                sum += element.ctc_actual
            if "cvc" in keys:
                sum += element.cvc_actual
            if "awc" in keys:
                sum += element.awc_actual
        return sum
