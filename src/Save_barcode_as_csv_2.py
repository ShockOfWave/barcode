def extract_list_from_raw_data(diagrams):
  ans = []
  for diagram in diagrams:
    ans.append([diagram[1][0], diagram[1][1], abs(diagram[1][0] - diagram[1][1]), diagram[0]])

  return ans

