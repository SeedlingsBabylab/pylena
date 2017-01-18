import datetime

from pylena import lena

#Create LenaRow class from "object" containing and specifying the attributes of the child
class LenaRow(object):
    def __init__(self, data_type="", child_key="", id="", last_name="",
                 first_name="", birth_date="", age="", sex="",
                 dlp="", processing_file="", timestamp="", duration="",
                 meaningful="", distant="", tv="", tv_percent=0,
                 noise="", silence="", awc_actual=0, ctc_actual=0,
                 cvc_actual=0, ava_stdscore=0, ava_stdscore_percent=0,
                 row_index=0):

    #Initialize variables in LenaRow class
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


#Create LenaRange class from "object"
class LenaRange(object):
    def __init__(self, group=None):
        for index, element in enumerate(group):
            if index == 0:
                continue
            #Check for ValueError in comparing element.row_index with group.row_index
            if element.row_index != group[index-1].row_index + 1:
                raise ValueError("lena range is not contiguous")

        #Assign variable self.range to value "group"
        self.range = group

    #Sum function that can be called from LenaRange class
    def sum(self, *keys):
        #Initialize sum variable to equal zero
        sum = 0
        #Loop through self.range (initialized above) - increment sum accordingly based on parameter "keys"
        for element in self.range:
            if "ctc" in keys:
                sum += element.ctc_actual
            if "cvc" in keys:
                sum += element.cvc_actual
            if "awc" in keys:
                sum += element.awc_actual
        return sum

    #Total_time function that can be called from LenaRange class
    def total_time(self, begin=0, end=None):
        #Check if indices are not out of range (Throw IndexError if they are out of range)
        if end > len(self.range) or begin > len(self.range)-1:
            raise IndexError("begin={}  end={}  were outside the range. Max index is {}"
                             .format(begin, end, len(self.range)))
        else:
            total_time = datetime.timedelta()
            if not begin and not end:
                begin = 0
                end = len(self.range)
            #Loop through range from begin to end
            for row in self.range[begin:end]:
                #initialize split_dur variable
                split_dur = map(int, row.duration.split(":"))
                #Update total_time variable using information from split_dur map
                total_time += datetime.timedelta(hours=split_dur[0], minutes=split_dur[1], seconds=split_dur[2])

            return total_time

    #get_range function that can be called from LenaRange class
    def get_range(self, begin=0, end=0):
        #Check to make sure indices are in range; if not in range- throw IndexError
        if end > len(self.range)-1 or begin > len(self.range)-1:
            raise IndexError("begin={}  end={} were outside the range. Max index is {}".format(begin, end, len(self.range)))
        else:
            #Set row_range and lena_range variables
            row_range = self.range[begin:end]
            lena_range = LenaRange(row_range)
            return lena_range

    #rank_window function that can be called from LenaRange class
    def rank_window(self, window_size, *keys):
        #Convert to all lowercase characters
        keys = [key.lower() for key in keys]
        for key in keys:
            #Check if key in lena.rank_keys- throw ValueError if not
            if key not in lena.rank_keys:
                raise ValueError("key: {}   not a valid ranking key".format(key))

        #Initialize start and end values
        start = 0
        end = window_size

        #Initialize region_values variable to empty list
        region_values = []

        window = self.get_range(start, end)

        #Continue through loop while end value is less than or equal to length of self.range - 1
        while end <= len(self.range)-1:
            #Calling the "sum" function written above in LenaRange class
            range_sum = window.sum(*keys)
            range_avg = float(range_sum) / window_size
            region_values.append((start, range_avg))

            #Update start and end variables to avoid infinite loop and update window in question
            start += 1
            end += 1

            #This if statement will only not execute the last time through the while loop
            if end <= len(self.range)-1:
                #Update window
                window = self.get_range(start, end)

        ranked_regions = sorted(region_values,
                                key=lambda region: region[1],
                                reverse=True)
        return ranked_regions

    #top_rows function
    def top_rows(self, n=5, *keys):
        keys = [key.lower() for key in keys]
        #Throw ValueError if key is not in lena.rank_keys; otherwise continue
        for key in keys:
            if key not in lena.rank_keys:
                raise ValueError("key: {}   not a valid ranking key".format(key))

        ranked = self.rank_window(1, *keys)

        return ranked[:n]




