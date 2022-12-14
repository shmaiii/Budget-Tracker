from imp import SEARCH_ERROR
from platform import architecture
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db import IntegrityError
from .models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        return HttpResponse("A user is logged in")
    return HttpResponse("No user is logged in ")
    


@csrf_exempt
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        data = json.loads(request.body)
        username = data.get("username", "")
        password = data.get("password", "")
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return JsonResponse({
                "logged_in": request.user.is_authenticated,
                "user": user.serialize(),
                "message": "Logged in as " + request.user.username
            }, safe=False)
        else:
            return JsonResponse({
                "message": "Invalid username and/or password.",
                "logged_in": False,
                "user": None,
            })
              
    elif request.method == 'GET':
        if request.user.is_authenticated:
            return JsonResponse({
                "logged_in": True,
                "user": request.user.serialize(),
                "message": "Logged in as " + request.user.username
            }, safe=False)
        else:
            return JsonResponse({
                "logged_in": False,
                "user": None,
                "message": "",
            })

@csrf_exempt
def register(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username", "")
        email = data.get("email", "")

        # Ensure password matches confirmation
        password = data.get("password", "")
        confirmation = data.get("confirmation" "")
        if password != confirmation:
            return JsonResponse({
                "message": "Passwords must match",
                "logged_in": False
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.expected_expense = Expense()
            user.actual_expense = Expense()
            user.save()
        except IntegrityError:
            return JsonResponse({
                "message": "Username already taken.",
                "logged_in": False
            })
    
    return JsonResponse({
            "message": "",
            "logged_in": False
        })
        

def logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))



def user_info(request, user_id):
    user = User.objects.get(pk=user_id)

    savings = user.savings
    reports = Report.objects.filter(owner_user=user)
    
    if request.method == 'GET':
        return JsonResponse({
            "deposits": user.total_deposit,
            "expected_expense": user.expected_expense.serialize(),
            "actual_expense": user.actual_expense.serialize(),
            "savings": savings,
            "reports": [report.serialze for report in reports]
        }, safe=False)
    
    #elif request.method == 'PUT':
    #    data = json.loads(request.body)
    #    if data.get("expected") is not None:
    #        user.expected_expense.groceries = data["groceries"]
    #        user.expected_expense.personal = data["personal"]
    #        user.expected_expense.mobile = data["mobile"]
    #        user.expected_expense.insurance = data["insurance"]
    #        user.expected_expense.housing = data["housing"]
    #        user.save()

     #       return HttpResponse(status=204)
    
    return JsonResponse({
        "error": "Not a GET or PUT request"
    }, status = 400)

@csrf_exempt
def user_info_put(request, user_id):

    user = User.objects.get(pk=user_id)

    savings = user.savings
    reports = Report.objects.filter(owner_user=user)

    if request.method == 'PUT':
        data = json.loads(request.body)
        if data.get("expected") is not None:
            expected = user.expected_expense

            if data.get("groceries") is not None:
                expected.groceries = data.get("groceries")
            if data.get("personal") is not None:
                expected.personal = data["personal"]
            if data.get("mobile") is not None:
                expected.mobile = data["mobile"]
            if data.get("insurance") is not None:
                expected.insurance = data["insurance"]
            if data.get("housing") is not None:
                expected.housing = data["housing"]
            expected.save()
            user.save()

            return HttpResponse(status=204)
        
        if (data.get("actual") is not None):
            expense = data["number"]
            category = data["category"]
            
            actual = user.actual_expense
            if category == "groceries":
                actual.groceries = actual.groceries + expense
            if category == "personal":
                actual.personal = actual.personal + expense
            if category == "mobile":
                actual.mobile = actual.mobile + expense
            if category == "insurance":
                actual.insurance = actual.insurance + expense
            if category == "housing":
                actual.housing =  actual.housing + expense
            actual.save()
            user.save()

            return HttpResponse(status=204)
        
        if (data.get("deposit") is not None):
            amountDeposit = data["amountDeposit"]
            user.total_deposit = user.total_deposit + amountDeposit
            user.save()

            return HttpResponse(status=204)
        
        if (data.get("saving") is not None):
            amountSaving = data["amountSaving"]
            user.savings = user.savings + amountSaving
            user.total_deposit = user.total_deposit - amountSaving
            user.save()
    
    return JsonResponse({
        "error": "Not a GET or PUT request"
    }, status = 400)
