# Stock Market Euphoria Predictor

Predicting next-day stock prices and detecting retail euphoria on the Indonesia Stock Exchange (IDX) using Twitter sentiment and a BiLSTM model with Bahdanau attention.

**Live app:** https://stock-market-euphoria-predictor.streamlit.app

## Introduction

Some IDX stocks go through short periods where the price climbs, trading volume jumps, and social media fills up with posts about them. Retail investors often buy near the top of these moves and lose money when the price falls back. Traders call this euphoria.

This project does two things:

1. Predicts the next-day closing price for 15 IDX stocks.
2. Flags days that match a euphoria pattern built from price, volume, and social media activity.

The idea being tested is whether adding what people say on Twitter, on top of price and volume, helps a sequence model read these episodes.

## Dataset

**Price data.** Daily OHLCV for 15 IDX tickers from 3 January 2022 to 30 December 2024, 16,395 rows. Two indicators are derived: a 20-day exponential moving average and a 14-day relative strength index.

**Text data.** 8,968 Indonesian tweets mentioning those tickers over the same period. 7,672 were annotated for sentiment by 3 annotators each, giving 23,016 labels.

**Tickers.** KARW, FORU, SRAJ, PANI, DSSA, SGER, TPIA, BRMS, MLPT, BRPT, TOBA, AUTO, IMAS, PSAB, KONI.

## Features

Eleven features per day, per stock:

| Group | Features |
|---|---|
| Price and volume | Open, High, Low, Close, Volume |
| Technical | RSI 14, price change %, volume change % |
| Social | daily tweet count, daily average sentiment |
| Flag | event flag (RSI extreme, volume spike, high tweet activity, or euphoria day) |

## How euphoria is labeled

Euphoria does not come as a label with the data, so it is defined by a rule. Each day is checked against four conditions:

| Condition | Meaning |
|---|---|
| Close at or above its 30-day average | price is running above trend |
| Volume at or above its 30-day average | unusual amount of trading |
| Tweet count at or above its 30-day average | more chatter than normal |
| Average sentiment at or above 0.50 | discussion is strongly positive |

**A day is labeled euphoric when at least 3 of the 4 conditions are met.** This produces 1,457 euphoric days, 8.84% of the dataset.

One caveat worth stating plainly: sentiment is scored from -1 to +1, so the 0.50 threshold is strict and only a small share of days clear it. In practice the label is driven mostly by the price, volume, and tweet-count conditions.

## Model

**Sentiment scoring.** IndoBERT (`indobert-base-p1`), fine-tuned on the SmSA Indonesian sentiment dataset, scores each tweet as P(positive) minus P(negative), between -1 and +1. Scores are averaged per stock per day. Days with no collected tweets get 0.

**Price prediction.** A bidirectional LSTM reads a 30-day window of the 11 features and predicts the next closing price. Two stacked layers, 128 hidden units, 25% dropout.

**Attention.** A Bahdanau attention layer sits on top. Instead of compressing 30 days into one vector, it learns a weight per day. That improves accuracy and lets us read afterwards which days the model leaned on.

**Euphoria classification.** A separate BiLSTM with the same attention mechanism outputs a euphoria probability per day. Because euphoric days are rare, SMOTE was applied to the training set to reach a 1:2 ratio between euphoric and non-euphoric samples.

## Train and test split

Sequences are ordered chronologically and split by time, never randomly, so the model cannot see the future.

| Split | Sequences | Period |
|---|---|---|
| Train | 12,756 (80%) | up to around 1 June 2024 |
| Test | 3,189 (20%) | around 1 June 2024 to 30 December 2024 |

The dataset ends on 30 December 2024. Nothing runs past that date, so the dashboard shows model output on held-out historical days, not forecasts of future dates.

## Results

Both models use the same 11 features. The comparison isolates the effect of the attention layer.

| Model | R2 | MAE (IDR) | RMSE (IDR) | MAPE |
|---|---|---|---|---|
| IndoBERT + BiLSTM + Attention (proposed) | 0.9985 | 125.47 | 361.15 | 2.69% |
| IndoBERT + LSTM (baseline, Yadav et al.) | 0.9983 | 135.30 | 386.52 | 3.04% |

A paired t-test on per-sample absolute errors gives t = 6.63, p = 1.9e-11, so the improvement is unlikely to be chance. Per-ticker results are on the Methodology page of the app.

The attention weights concentrate on the most recent lags in the 30-day window and drop off for older days, which is what you would expect when predicting the next close.

## Dashboard

Built with Streamlit. Three pages.

**Stock Analysis.** Price chart with candlestick or line view, EMA20, RSI, volume, and daily tweet counts, with euphoria days marked. A side panel shows the euphoria probability for the most recent day, the IndoBERT sentiment score, a log of the 10 most recent model outputs, and the full list of euphoria signals.

**Euphoria Drill-Through.** Pick any signal date and inspect it: how the day compares to its own 30-day average on price, volume, and tweet count; the day change and 5-day return; the classifier output; and the same-day sentiment.

**Market Screener.** All 15 stocks with their values on the final trading day, plus a chart counting euphoria signals per stock across the held-out period.

**Methodology.** Model description, performance tables, the significance test, and the attention weight chart.

## Reading the dashboard

A few things worth knowing before interpreting the numbers.

**Euphoria probability does not track the sentiment score.** The classifier reads 30 days of all 11 features at once. Sentiment is one input among many, and in this dataset the signal is driven mostly by price and volume behaviour. A day can carry a high probability while same-day sentiment is flat or negative.

**A sentiment of 0.000 can mean two different things.** Either the tweets that day averaged out to neutral, or no tweets were collected for that stock that day and the feature defaulted to zero. The drill-through view says which one applies.

**Tweet coverage is uneven.** Heavily discussed stocks like BRPT, BRMS, and TPIA have over 1,300 tweets each, while KONI has 122. Thinly covered stocks can produce euphoria signals with little or no text on the day itself.

**The screener is a snapshot.** It shows the final trading day in the dataset, which was calm across all 15 stocks. The signal count chart below it shows activity across the whole held-out period.

## Running it locally

```bash
git clone https://github.com/mike21ai/Stock-Market-Euphoria-Predictor.git
cd Stock-Market-Euphoria-Predictor
pip install -r requirements.txt
streamlit run app.py
```

These files must sit next to `app.py`:

- `Streamlit_Daily_Data.csv` - daily price data with model outputs
- `Streamlit_Methodology_Data.json` - evaluation metrics and attention weights

Keep the CSV as UTF-8 with comma separators. Opening and re-saving it in Excel under an Indonesian locale can switch the separator to a semicolon and break the column names.

## Repository contents

| File | Purpose |
|---|---|
| `app.py` | Streamlit dashboard |
| `stock_market_euphoria_prediction.py` | full training and evaluation notebook, exported to Python |
| `Streamlit_Daily_Data.csv` | daily data with model outputs |
| `Streamlit_Methodology_Data.json` | metrics and attention weights |
| `Streamlit_Tweet_Feed.csv` | raw tweet corpus, kept for reference |
| `Dataset_Tweet_dan_Harga_Saham.xlsx` | source data |
| `requirements.txt` | dependencies |

## Requirements

```
streamlit
pandas
numpy
plotly
pytz
```

## Limitations

- The data ends in December 2024, so the app runs on historical data. It is not connected to a live feed.
- Tweets were collected by matching ticker strings, which picks up unrelated posts for tickers that are also ordinary words. FORU collides with the "for you" hashtag and with a company of a similar name; AUTO collides with the Indonesian adverb "auto". Annotation filtered these, but coverage per stock is still uneven.
- The euphoria rule is a definition, not ground truth. Different thresholds would flag different days.
- Both the proposed and baseline models include sentiment as an input, so the results measure the effect of attention, not the effect of sentiment. No ablation without sentiment was run.
- Sentiment on any single day may be averaged from only one or two tweets, so daily scores are noisy for thinly covered stocks.

## Disclaimer

This is a research project for a master's thesis. Nothing here is financial advice.
