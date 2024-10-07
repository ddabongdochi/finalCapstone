# # dashboard/views.py
# import os
#
# from django.shortcuts import render
# from dotenv import load_dotenv
#
# from .models import Stock
# from django.utils import timezone
# import mojito
# import pprint
#
# def dashboard(request):
#     load_dotenv()
#
#     # 임시 데이터 생성
#     mock_stocks = [
#         {'symbol': 'AAPL', 'name': 'Apple Inc.', 'current_price': 150.25, 'last_updated': timezone.now()},
#         {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'current_price': 2750.80, 'last_updated': timezone.now()},
#         {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'current_price': 305.50, 'last_updated': timezone.now()},
#         {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'current_price': 3380.75, 'last_updated': timezone.now()},
#         {'symbol': 'FB', 'name': 'Facebook, Inc.', 'current_price': 330.20, 'last_updated': timezone.now()},
#     ]
#
#     # 총 포트폴리오 가치 계산
#     # total_value = sum(stock['current_price'] for stock in mock_stocks)
#
#
#     broker = mojito.KoreaInvestment(
#         api_key=os.getenv('api_key'),
#         api_secret=os.getenv('api_secret'),
#         acc_no=os.getenv('acc_no'),
#         mock=True
#
#     )
#     resp = broker.fetch_balance()
#
#     total_value = resp['output2'][0]['tot_evlu_amt']
#     print(resp['output2'][0]['tot_evlu_amt'])
#     pprint.pprint(resp)
#     context = {
#         'acc_no': "50117588-01",
#         'stocks': mock_stocks,
#         'total_value': total_value,
#         'total_stocks': len(mock_stocks),
#     }
#
#
#     # test()
#     return render(request, 'dashboard/dashboard.html', context)
#
#
# def test():
#
#
#     # with open("../../koreainvestment.key") as f:
#     #     lines = f.readlines()
#     #
#     # key = lines[0].strip()
#     # secret = lines[1].strip()
#     # acc_no = lines[2].strip()
#
#     broker = mojito.KoreaInvestment(
#         api_key="PS2osgVtJebLijhOGFbRwYiw9lKwXQfK8PEk",
#         api_secret="TcmO8QRKiSVA+ZQIV8+mXXYdbPM1iMVZrChj5X4Pi83EhBV2YLlPDnWsn5zfi3OCLyQ1quEoBYpH262PxWlbSVPuA7YaSR5MGGnE9/cCter0+CY9jfGH/sbkdIgF/fCjgi5zKLg1J84lpuAy+Dr6UCAWfvtnkXLnkZuPKB5Jz+gsmp/arVE=",
#         acc_no="50117588-01"
#     )
#     resp = broker.fetch_balance()
#     pprint.pprint(resp)
#
#
from django.shortcuts import render
from dotenv import load_dotenv
from .models import Stock
import os
import mojito
import pprint


def dashboard(request):
    load_dotenv()

    broker = mojito.KoreaInvestment(
        api_key=os.getenv('api_key'),
        api_secret=os.getenv('api_secret'),
        acc_no=os.getenv('acc_no'),
        mock=False
    )

    try:
        # Fetch stock balance from Mojito API
        resp = broker.fetch_balance()

        # 디버그: 응답 전체 구조를 출력해서 확인
        pprint.pprint(resp)

        # 'access_token'이 응답에 존재하는지 확인
        if 'access_token' not in resp:
            raise KeyError("Response does not contain 'access_token'")

        # Parse the response to extract stock information
        stocks = []
        output1 = resp.get('output1', [])

        for stock_info in output1:
            stock = {
                'symbol': stock_info.get('pdno', 'N/A'),
                'name': stock_info.get('prdt_name', 'N/A'),
                'current_price': float(stock_info.get('evlu_pfls_amt', 0)),
                'last_updated': timezone.now()
            }
            stocks.append(stock)

        # Calculate total portfolio value
        output2 = resp.get('output2', [{}])
        total_value = output2[0].get('tot_evlu_amt', 0)

    except KeyError as e:
        print(f"KeyError: {e}")  # 에러 로그 출력
        return render(request, 'dashboard/error.html', {'error': "API 응답에 문제가 발생했습니다."})
    except Exception as e:
        print(f"Error fetching balance: {e}")
        return render(request, 'dashboard/error.html', {'error': str(e)})

    context = {
        'acc_no': os.getenv('acc_no'),
        'stocks': stocks,
        'total_value': total_value,
        'total_stocks': len(stocks)
    }

    return render(request, 'dashboard/dashboard.html', context)



