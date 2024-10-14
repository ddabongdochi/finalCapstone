import os
from django.shortcuts import render
from dotenv import load_dotenv
from .models import Stock
from django.utils import timezone
import mojito


def dashboard(request):
    load_dotenv()

    # 주식 API 데이터 가져오기
    broker = mojito.KoreaInvestment(
        api_key=os.getenv('api_key'),
        api_secret=os.getenv('api_secret'),
        acc_no=os.getenv('acc_no'),
        exchange='나스닥',
        mock=True
    )

    balance = broker.fetch_present_balance()
    stock_holdings = []
    total_value = 0

    # print(balance)

    for comp in balance['output1']:
        stock_holdings.append({
            'symbol': comp['pdno'],
            'name': comp['prdt_name'],
            'country': comp['natn_kor_name'],
            'exchange_code': comp['ovrs_excg_cd'],
            'market_name': comp['tr_mket_name'],

            'profit_loss_rate': float(comp['evlu_pfls_rt1']),

            'exchange_rate': float(comp['bass_exrt']),
            'purchase_amount_foreign': float(comp['frcr_pchs_amt']),
            'last_updated': timezone.now(),

        })

    total_value = balance['output3'].get('tot_asst_amt', 0)

    PnL = balance['output3'].get('tot_evlu_pfls_amt')


    # print(PnL)

    context = {
        'acc_no': os.getenv('acc_no'),
        'stocks': stock_holdings,
        'total_value': total_value,
        'total_stocks': len(stock_holdings),
        'PnL': float(PnL)
    }

    return render(request, 'dashboard/dashboard.html', context)


# def ROI(request):
#     return render(request,"dashboard/views.py")
