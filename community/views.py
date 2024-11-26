from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from login.models import UserProfile


# Create your views here.

@login_required
def community(request):
    stock_symbol = request.GET.get('symbol', 'Unknown')
    stock_name = request.GET.get('name', 'Unknown Stock')
    return render(request, 'community/community.html', {
        'stock_symbol': stock_symbol,
        'stock_name': stock_name,
    })
