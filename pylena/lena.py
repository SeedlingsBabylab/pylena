import csv
import datetime

from pylena import elements

rank_keys = ["ctc", "cvc", "awc"]

#Create LenaFile class
class LenaFile:
    def __init__(self, lena_file=""):
        self.range = []

        if lena_file:
            #Open lena_file for reading
            with open(lena_file, "rU") as input:
                #Initialize and incrememnt "reader" to traverse the lena_file
                reader = csv.reader(input)
                reader.next()
                #Loop through row in file assigning values to variables
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

                    #Set lena_row variable calling using LenaRow class from elements.py
                    #Using variables initialized above
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

            #Initialize child_keys and child_key_set variables
            child_keys = [element.child_key for element in self.range]
            child_key_set = set(child_keys)
            #If only one element in child_key_set
            if len(child_key_set) == 1:
                self.child_key = child_key_set.pop()

            #Initialize sexes variable and sex_set variable
            sexes = [element.sex for element in self.range]
            sex_set = set(sexes)
            #If only one element in sex_set
            if len(sex_set) == 1:
                self.sex = sex_set.pop()

            #Initialize birthdates variable and birth_set variable
            birthdates = [element.birth_date for element in self.range]
            birth_set = set(birthdates)
            #If only one element in birth_set
            if len(birth_set) == 1:
                self.birth_date = birth_set.pop()

            #Initialize ages variable and age_set variable
            ages = [element.age for element in self.range]
            age_set = set(ages)
            #If only one element in age_set
            if len(age_set) == 1:
                self.age = age_set.pop()

    #get_range function in LenaFile class (used in elements.py)
    def get_range(self, begin=0, end=0):
        #Check to make sure indices are in range; throw IndexError if not
        if end > len(self.range)-1 or begin > len(self.range)-1:
            raise IndexError("begin={}  end={} were outside the range. Max index is {}".format(begin, end, len(self.range)))
        else:
            #Use LenaRange class from elements.py in returning lena_range
            row_range = self.range[begin:end]
            lena_range = elements.LenaRange(row_range)
            return lena_range

    #get_rows function in LenaFiles class
    def get_rows(self, rows):
        """
        :param rows: a list of indices e.g. [1, 44, 65, 87, 9]
        :return: a list of LenaRow corresponding to those indices
        """
        if not rows:
            raise ValueError("you need to privide a list of indices to retrieve those rows")
        else:
            #Initialize results list to empty list
            results = []
            #Loop through rows
            for index in rows:
                #Check to make sure indices are in range; throw IndexError if not in range
                if len(self.range)-1 < index:
                    raise IndexError("the index: {}   is out of bounds. Max index is {}".format(index, len(self.range)))
                else:
                    #If index is in range; append self.range[index] to results list
                    results.append(self.range[index])
        return results

    #rank_window function in LenaFiles class
    def rank_window(self, window_size, *keys):
        keys = [key.lower() for key in keys]
        for key in keys:
            #Check if key is in rank_keys; throw ValueError if not;
            if key not in rank_keys:
                raise ValueError("key: {}   not a valid ranking key".format(key))

        #Initialize variables start and end to be used in the while loop
        start = 0
        end = window_size

        #Initialize region_values to empty list
        region_values = []

        window = self.get_range(start, end)

        #Run the while loop as long as "end" variable is less than or equal to length of self.range - 1
        while end <= len(self.range)-1:
            #Set range_sum variable to be used in calculating range_avg
            range_sum = window.sum(*keys)
            #Set range_avg variable to be appended to range_values list
            range_avg = float(range_sum) / window_size
            region_values.append((start, range_avg))

            #Increment start and end variables to avoid infinite loop and to update window
            start += 1
            end += 1

            #Update window being observed
            if end <= len(self.range)-1:
                window = self.get_range(start, end)

        ranked_regions = sorted(region_values,
                                key=lambda region: region[1],
                                reverse=True)
        return ranked_regions

    #top_rows function in LenaFile class
    def top_rows(self, n=5, *keys):
        keys = [key.lower() for key in keys]
        for key in keys:
            #Check if key in rank_keys and throw ValueError if not
            if key not in rank_keys:
                raise ValueError("key: {}   not a valid ranking key".format(key))

        #Initialize variable "ranked"
        ranked = self.rank_window(1, *keys)

        return ranked[:n]

    #total_time function in LenaFile class
    def total_time(self, begin=0, end=None):
        #Check if indices are in range; throw IndexError if not in range
        if end > len(self.range) or begin > len(self.range)-1:
            raise IndexError("begin={}  end={}  were outside the range. Max index is {}"
                             .format(begin, end, len(self.range)))
        #Update total_time being calculated
        else:
            total_time = datetime.timedelta()
            if not begin and not end:
                begin = 0
                end = len(self.range)
            #Loop through rows in self.range[begin:end]
            for row in self.range[begin:end]:
                split_dur = map(int, row.duration.split(":"))
                #Update total time using values from split_dur map initialized and updated above
                total_time += datetime.timedelta(hours=split_dur[0], minutes=split_dur[1], seconds=split_dur[2])

            return total_time
    #sum function in LenaFile class
    def sum(self, *keys):
        #Initialize sum to zero
        sum = 0
        #Loop through elements in self.range; updating total_time accordingly based on the strings present in "keys"
        for element in self.range:
            if "ctc" in keys:
                sum += element.ctc_actual
            if "cvc" in keys:
                sum += element.cvc_actual
            if "awc" in keys:
                sum += element.awc_actual
        return sum
