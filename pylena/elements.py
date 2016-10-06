import datetime

from pylena import lena

class LenaRow(object):
    def __init__(self, data_type="", child_key="", id="", last_name="",
                 first_name="", birth_date="", age="", sex="",
                 dlp="", processing_file="", timestamp="", duration="",
                 meaningful="", distant="", tv="", tv_percent=0,
                 noise="", silence="", awc_actual=0, ctc_actual=0,
                 cvc_actual=0, ava_stdscore=0, ava_stdscore_percent=0,
                 row_index=0):

        self.data_type = data_type
        self.child_key = child_key
        self.id = id
        self.last_name = last_name
        self.first_name = first_name
        self.birth_date = birth_date
        self.age = age
        self.sex = sex
        self.dlp = dlp
        self.processing_file = processing_file
        self.timestamp = timestamp
        self.duration = duration
        self.meaningful = meaningful
        self.distant = distant
        self.tv = tv
        self.tv_percent = tv_percent
        self.noise = noise
        self.silence = silence
        self.awc_actual = awc_actual
        self.ctc_actual = ctc_actual
        self.cvc_actual = cvc_actual
        self.ava_stdscore = ava_stdscore
        self.ava_stdscore_percent = ava_stdscore_percent
        self.row_index = row_index



class LenaRange(object):
    def __init__(self, group=None):
        for index, element in enumerate(group):
            if index == 0:
                continue
            if element.row_index != group[index-1].row_index + 1:
                raise ValueError("lena range is not contiguous")

        self.range = group

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

    def get_range(self, begin=0, end=0):
        if end > len(self.range)-1 or begin > len(self.range)-1:
            raise IndexError("begin={}  end={} were outside the range. Max index is {}".format(begin, end, len(self.range)))
        else:
            row_range = self.range[begin:end]
            lena_range = LenaRange(row_range)
            return lena_range

    def rank_window(self, window_size, *keys):
        keys = [key.lower() for key in keys]
        for key in keys:
            if key not in lena.rank_keys:
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
            if key not in lena.rank_keys:
                raise ValueError("key: {}   not a valid ranking key".format(key))

        ranked = self.rank_window(1, *keys)

        return ranked[:n]




