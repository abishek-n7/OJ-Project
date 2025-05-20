from django.shortcuts import render

# Create your views here.

def contest_page(request):
    return render(request, 'contest_page.html')