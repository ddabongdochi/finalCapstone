from django.shortcuts import render
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from torch.autograd import Variable

# 한국 시간대 설정
korea_tz = pytz.timezone('Asia/Seoul')

# Yahoo Finance API로 실제 주가 가져오기
def get_actual_price(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d", interval="1m")  # 1분 단위로 오늘 날짜의 데이터를 가져옵니다.

    if not hist.empty:
        actual_price = hist['Close'].iloc[-1]  # 가장 최신 종가를 가져옵니다.
        return float(actual_price)
    else:
        return None

# Yahoo Finance API로 시퀀스 데이터 가져오기
def get_sequence_data(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="5d", interval="5m")  # 5일간의 5분 단위 데이터를 가져옵니다.

    if not hist.empty:
        sequence_data = hist['Close'].tolist()
        return sequence_data
    else:
        return None

# Bidirectional LSTM 모델 정의
class BiLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, dropout=0.2):
        super(BiLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout, bidirectional=True)
        self.fc = nn.Linear(hidden_size * 2, 1)  # 양방향 출력을 고려하여 hidden_size 두 배로 설정

    def forward(self, x):
        h_0 = Variable(torch.zeros(self.num_layers * 2, x.size(0), self.hidden_size))  # * 2 for bidirection
        c_0 = Variable(torch.zeros(self.num_layers * 2, x.size(0), self.hidden_size))  # * 2 for bidirection
        output, (hn, _) = self.lstm(x, (h_0, c_0))
        out = self.fc(torch.cat((hn[-2], hn[-1]), dim=1))  # 양방향 마지막 상태 결합
        return out

def predict_stock_price(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        time_interval = int(request.POST.get('time_interval'))  # 5, 15, 30, 60 (분 단위)

        # 시퀀스 데이터 가져오기
        sequence_data = get_sequence_data(symbol)
        if sequence_data is None:
            return render(request, 'prediction/prediction_error.html', {'message': '실시간 주가 시퀀스를 가져오는 데 실패했습니다.'})

        # 실제 주가 가져오기
        actual_price = get_actual_price(symbol)
        if actual_price is None:
            return render(request, 'prediction/prediction_error.html', {'message': '실제 주가를 가져오는 데 실패했습니다.'})

        # 데이터 전처리
        scaler = MinMaxScaler()
        sequence_data = [[price] for price in sequence_data]

        if len(sequence_data) <= 30:
            return render(request, 'prediction/prediction_error.html', {'message': '데이터가 부족하여 예측을 할 수 없습니다. 더 많은 데이터가 필요합니다.'})

        scaled_data = scaler.fit_transform(sequence_data)

        # 시퀀스 설정 및 텐서 변환
        sequence_length = 30
        X_seq = [scaled_data[i:i + sequence_length] for i in range(len(scaled_data) - sequence_length)]
        if len(X_seq) == 0:
            return render(request, 'prediction/prediction_error.html', {'message': '시퀀스 데이터 생성에 실패했습니다.'})

        X_tensors = torch.Tensor(X_seq)

        # 모델 초기화
        input_size = 1
        hidden_size = 50
        num_layers = 2
        model = BiLSTM(input_size, hidden_size, num_layers)

        if len(X_tensors) > 0:
            future_X = X_tensors[-1].view(1, sequence_length, -1)

            # 예측
            with torch.no_grad():
                future_pred = model(future_X).detach().numpy()

            predicted_price = scaler.inverse_transform(future_pred)[0, 0]
        else:
            return render(request, 'prediction/prediction_error.html', {'message': '예측을 위한 유효한 데이터가 없습니다.'})

        # 현재 시간 계산
        end_time = datetime.now(korea_tz)
        prediction_time = end_time + timedelta(minutes=time_interval)

        context = {
            'symbol': symbol,
            'predicted_price': predicted_price,
            'prediction_time': prediction_time.strftime('%Y-%m-%d %H:%M'),
            'actual_price': actual_price,
        }

        return render(request, 'prediction/prediction_result.html', context)
    else:
        return render(request, 'prediction/prediction_form.html')
