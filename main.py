import requests
import pandas as pd
import time, json

replacement = str.maketrans({"&" : "%26", "(" : "%28", ")" : "%29", "/" : '-', "|" : "%7C"})

session = requests.Session()
session.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def parse_price(name : str):
  name = name.translate(replacement)
  name = name.split(' ')
  url = 'https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name=' #Currency=1 for $ if you need euro use currency=3
  item_hash_name = '%20'.join(name) #create hash name
  url +=item_hash_name
  response = session.get(url=url)
  data = json.loads(response.text)
  return data["lowest_price"] if data['success']==True else url


def main():
  df = pd.read_excel('table.xlsx')
  last_raw = df.iloc[-1]
  if type(last_raw["Name"]) is float:
    df = df.drop(index=df.index[-1])
  for index,row in df.iterrows():
    try:
      price = parse_price(row['Name'])
      df.loc[index,"Price/Unit"] = price
      df.loc[index, "Total"] = float(price[1:])*int(row["Amount"])
      time.sleep(5)
    except ValueError:
      print(f"This item {row['Name']} not found!")
  sum_row = pd.DataFrame({'Total': df["Total"].sum()}, index=[len(df)])
  # append the new rows to the dataframe
  df = df.append(sum_row)
  df.to_excel('table.xlsx', index=False)  #Save to the Excell file

if __name__=="__main__":
  main()