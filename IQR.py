from numpy import percentile

def iqr_filter(data, cutoff):
  """
  Perfrom IQR filtering on a list of data.

  Parameters:
  data - The list of data to be filtered
  cutoff - The IQR factor that estiblishes the cutoff limits.
           Use 1.5 for robust filtering; 3.0 to remove exterem outliers.

  Returns: ([kept data], [removed data])
  """

  # calculate interquartile range
  q25, q75 = percentile(data, 25), percentile(data, 75)
  iqr = q75 - q25
  # calculate the outlier cutoff
  cut_off = iqr * cutoff
  lower, upper = q25 - cut_off, q75 + cut_off
  # identify outliers
  outliers = [x for x in data if x < lower or x > upper]
  # remove outliers
  outliers_removed = [x for x in data if x >= lower and x <= upper]

  return (outliers_removed, outliers)

def test(data, cutoff):
  (clean_data, outliers) = iqr_filter(data, cutoff)
  print("--- Cutoff:", cutoff, "---")
  print("Data:", data)
  print("Clean:", clean_data)
  print("Outliers:", outliers)
  print()


if __name__ == '__main__':
  print("IRQ Demo")

  data = [13, 13, 13, 14, 16, 13, 14, 14, 13, 18, 12, 12, 14, 14, 11, 11, 11, 14, 12, 12, 14, 11, 14, 14, 32780, 14, 12, 11, 11, 13]
  test(data, 1.5)
  test(data, 3.0)

  data = [438, 422, 405, 400, 400, 400, 414, 433, 33201, 461, 473, 463, 478, 481, 481, 473, 463, 456, 447, 447, 442, 427, 417, 417, 405, 414, 400, 400, 400, 407]
  test(data, 1.5)
  test(data, 3.0)

  data = [65535, 422, 405, 400, 400, 400, 414, 433, 33201, 461, 473, 463, 478, 481, 481, 473, 463, 456, 447, 447, 442, 427, 417, 417, 405, 414, 400, 400, 400, 407]
  test(data, 1.5)
  test(data, 3.0)

