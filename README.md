# Euphoria Predictor Terminal

Predicting stock price and detecting retail euphoria on the Indonesia Stock Exchange (IDX) using Twitter sentiment and a BiLSTM model with attention.

**Live app:** https://stock-market-euphoria-predictor.streamlit.app

## Introduction

Some IDX stocks go through short periods where the price jumps, trading volume explodes, and social media suddenly fills up with posts about them. Retail investors often buy in at the top of these moves and lose money when the price falls back. Traders call this euphoria.

This project does two things:

1. Predicts the next day closing price for 15 IDX stocks.
2. Flags days where price, volume, and social media activity all point to euphoria.

The main idea is that price data alone misses what is happening. Adding what people are saying on Twitter gives the model information that the chart does not contain yet.

## Dataset

**Price data.** Daily OHLCV for 15 IDX tickers from January 2022 to December 2024, 16,395 rows in total. Two indicators are added: a 20 day exponential moving average (EMA20) and a 14 day relative strength index (RSI14).

**Text data.** 8,968 Indonesian tweets mentioning those tickers over the same period. 7,672 of them were labelled for sentiment by 3 annotators each, giving 23,016 labels.

**Tickers.** KARW, FORU, SRAJ, PANI, DSSA, SGER, TPIA, BRMS, MLPT, BRPT, TOBA, AUTO, IMAS, PSAB, KONI.

The model is evaluated on June to December 2024, which is held out from training.

## How euphoria is defined

Euphoria is not a label that comes with the data, so it is defined by a rule. A day is marked as euphoric when all four of these hold:

| Condition | Meaning |
|---|---|
| Close price at or above its 30 day average | Price is running hot |
| Volume at or above its 30 day average | Unusual amount of trading |
| IndoBERT sentiment at or above 0.50 | People are talking positively |
| Tweet count at or above its 30 day average | More chatter than normal |

The dashboard shows which of the four conditions were met on any given day, so the signal can be checked instead of taken on trust.

## Features used by the model

- Price and volume: Open, High, Low, Close, Volume
- Technical: EMA20, RSI14
- Social: daily average sentiment score, daily tweet count

## Model

**Sentiment scoring.** IndoBERT, a BERT model pre-trained on Indonesian text, is fine tuned on the labelled tweets. Each tweet gets a sentiment score, and the scores are averaged per stock per day.

**Price prediction.** A bidirectional LSTM reads a 30 day window of the features above and predicts the next closing price. Reading the sequence in both directions lets the model pick up both momentum and pullbacks.

**Attention.** A Bahdanau attention layer sits on top of the LSTM. Instead of squeezing 30 days into one vector, it learns a weight for each day. This is useful for two reasons: it improves accuracy, and the weights can be read afterwards to see which days the model actually relied on.

## Results

Compared against an IndoBERT + LSTM baseline (Yadav et al.) with no attention layer:

| Model | R2 | MAE (IDR) | RMSE (IDR) | MAPE |
|---|---|---|---|---|
| IndoBERT + BiLSTM + Attention (this work) | 0.9985 | 125.47 | 361.15 | 2.69% |
| IndoBERT + LSTM (baseline) | 0.9983 | 135.30 | 386.52 | 3.04% |

The gap is small in absolute terms but consistent. A paired t-test on the per sample errors gives t = 6.63 and p = 1.9e-11, so the improvement is not down to chance. Per ticker results are in the Methodology page of the app.

## What the attention weights show

The attention layer puts most of its weight on the most recent days in the window and very little on days further back. The baseline spreads its attention almost evenly across all 30 days. This lines up with how euphoria actually behaves: it builds over a few days, not a few months.

## Dashboard

Built with Streamlit. Three pages:

**Stock Analysis.** Price chart with candlestick or line view, EMA20, RSI, volume, and daily tweet counts. Euphoria days are marked on the chart. A side panel shows the predicted euphoria probability, the next day price forecast, the IndoBERT sentiment score, and a log of recent predictions.

**Euphoria Drill-Through.** Pick any euphoria date and see why it was flagged: which of the four rule conditions were met, the day change and 5 day return, the volume, the tweet count against its average, and the sentiment score.

**Market Screener.** All 15 stocks in one table with their latest prices, sentiment, and euphoria probability, plus a bar chart comparing probabilities across stocks.

**Methodology.** Model description, the performance tables above, the significance test, and the attention weight chart.

A note on the tweet display: the dashboard shows aggregated tweet counts and sentiment rather than individual tweets. The euphoria signal is computed from 30 day aggregates, so showing single posts from one date would misrepresent how the model works.

## Running it locally

```bash
git clone <repo-url>
cd <repo-folder>
pip install -r requirements.txt
streamlit run app.py
```

These files need to be in the same folder as `app.py`:

- `Streamlit_Daily_Data.csv` - daily price data with model outputs
- `Streamlit_Methodology_Data.json` - evaluation metrics and attention weights
- `Streamlit_Tweet_Feed.csv` - raw tweet corpus, kept for reference

## Requirements

```
streamlit
pandas
numpy
plotly
pytz
```

## Limitations

- The data stops at December 2024, so the app runs on historical data rather than live prices.
- The tweet corpus was collected by matching ticker strings, which picks up unrelated posts for tickers that are also common words. This was handled during annotation but is worth knowing about.
- The euphoria rule is a definition, not ground truth. Different thresholds would flag different days.

## Disclaimer

This is a research project. Nothing here is financial advice.
