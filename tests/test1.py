import pylena



if __name__ == "__main__":

    lena_file = pylena.LenaFile("02_07_lena5min.csv")

    lena_range = lena_file.get_range(0, 5)


    row1 = lena_range.range[0]

    print lena_range.total_time()

    sum_ctc = lena_range.sum("ctc")

    sum_ctc_cvc = lena_range.sum("ctc", "cvc")

    ranked_regions = lena_file.rank_window(4, "CTC", "cvc")

    top_ranked_5 = lena_file.top_rows(5, "ctc", "cvc")

    the_rows = lena_file.get_rows([element[0] for element in top_ranked_5])

    time = lena_file.total_time(0, 5)
    time2 = lena_file.total_time()

