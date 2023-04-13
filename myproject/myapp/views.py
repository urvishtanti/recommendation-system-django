import array
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from .models import Restaurent,Cusine
from django.contrib.auth.models import User
from django.contrib import messages
import pandas as pd
import numpy as np
import operator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Similarity
from sklearn.metrics.pairwise import cosine_similarity

def my_app(request):
    restaurents = Restaurent.objects.all()[:5]
    cusines = Cusine.objects.all()[:5]
    return render(request, 'myapp/index.html', {'restaurents': restaurents, 'cusines': cusines})



def login_decor(pass_function):
    def login_func(request):
        if request.user.is_authenticated:
            print("User is authenticated")
            if str(request.get_full_path()) == '/login/':
                print("Logging out")
                logout(request)
            return pass_function(request)
        elif request.method == 'POST':
            userID = request.POST.get('userid')
            password = request.POST.get('password')
            user = authenticate(request, username=userID, password=password)
            if user is not None:
                login(request, user)
                return redirect('/recommend/') # redirect to home page after successful login
            else:
                # handle invalid login credentials
                return redirect('/login/')
        return render(request, 'myapp/login.html')
    return login_func 

@login_decor
def login_f(request):
    return render(request, 'myapp/login.html')


def registration_view(request):
    if request.method == 'POST':
        # get the form data from the POST request
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        # check if the username and email are unique
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        # create a new user object
        user = User.objects.create_user(username=username, email=email, password=password)
        print(user)

        # log the user in and redirect to the home page
        login(request, user)
        messages.success(request, 'You have registered successfully')
        return redirect('/recommend')
    else:
        return render(request, 'myapp/signup.html')

@login_decor
def recommend(request,number_of_similar_items=130):
    page = request.GET.get('page', 1)
    TestArray = []

    if not Restaurent.objects.filter(userID=request.user).exists():
       TestArray =  new_recommend(request,TestArray,number_of_similar_items=130)
    else:
        ratings = Restaurent.objects.all().order_by('userID', 'placeID').values()
        ratings = pd.DataFrame.from_records(ratings)
        current_user = request.user
        ratings.head()
        df=ratings
        matrix = df.pivot_table(index='placeID', columns='userID', values='total_rating')
        matrix.head()
        matrix_norm = matrix.subtract(matrix.mean(axis=1), axis = 0)
        matrix_norm.head()
        item_similarity_cosine = cosine_similarity(matrix_norm.fillna(0))
        item_similarity_cosine_matrix=pd.DataFrame(item_similarity_cosine)
        item_similarity_cosine_matrix.head()
        item_similarity_cosine_matrix.replace(0, np.nan, inplace=True)
        item_similarity_cosine_matrix.columns = matrix_norm.index
        item_similarity_cosine_matrix['placeID'] = matrix_norm.index
        item_similarity_cosine_matrix = item_similarity_cosine_matrix.set_index('placeID')
        item_similarity_cosine_matrix.head()
        
        picked_userid_notvisited = pd.DataFrame(matrix_norm[current_user.username].isna()).reset_index()
        picked_userid_notvisited = picked_userid_notvisited[picked_userid_notvisited[current_user.username]==True]['placeID'].values.tolist()
        picked_userid_visited = pd.DataFrame(matrix_norm[current_user.username].dropna(axis=0, how='all')\
                                .sort_values(ascending=False))\
                                .reset_index()\
                                .rename(columns={current_user.username:'rating'})
        rating_prediction ={} 
        for picked_restraunt in picked_userid_notvisited: 
            picked_restraunt_similarity_score = item_similarity_cosine_matrix[[picked_restraunt]].reset_index().rename(columns={picked_restraunt:'similarity_score'})
            picked_userid_visited_similarity = pd.merge(left=picked_userid_visited, 
                                                        right=picked_restraunt_similarity_score, 
                                                        on='placeID', 
                                                        how='inner')\
                                                .sort_values('similarity_score', ascending=False)[:number_of_similar_items]
            predicted_rating = round(np.average(picked_userid_visited_similarity['rating'], 
                                                weights=picked_userid_visited_similarity['similarity_score']), 6)
            rating_prediction[picked_restraunt] = predicted_rating 
        key = pd.DataFrame.from_dict(rating_prediction,orient='index').sort_values(by=0, ascending=False).dropna()[0].keys().tolist()
        print(key)
        if len(key) == 0:
            TestArray =  new_recommend(request,TestArray,number_of_similar_items=130)

        for i in range(len(key)):
            str = Cusine.objects.filter(placeID=key[i]).values()
            if not str:
                TestArray.append(key[i]) 
            else:
                TestArray.append(str) 
    paginator = Paginator(TestArray, 5)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    return render(request,'myapp/recommendation.html',{'value':data})

def new_recommend(request,TestArray,number_of_similar_items=130):
    ratings = Restaurent.objects.all().order_by('total_rating', 'placeID').values()
    ratings = pd.DataFrame.from_records(ratings)
    key = ratings.sort_values(by='total_rating', ascending=False).dropna(subset=['total_rating'])['placeID'].tolist()
    unique_key = list(set(key)) 
    for i in range(len(unique_key)):
        str = Cusine.objects.filter(placeID=unique_key[i]).values()
        if not str:
            TestArray.append(unique_key[i]) 
        else:
            TestArray.append(str)
    return TestArray
    
        
@login_decor
def addrating(request):
    placeID =request.GET.get('placeID')
    context ={'placeID': placeID}
    return render(request,'myapp/addrating.html',context)

@login_decor
def submitrating(request):
    if request.method=='POST':
        placeID = request.POST.get('placeID')
        rating = request.POST.get('rating')
        food_rating = request.POST.get('food_rating')
        service_rating = request.POST.get('service_rating')
        current_user = request.user
        total_rating = int(rating) + int(food_rating) + int(service_rating)
        restaurant = Restaurent(userID = current_user,placeID = placeID, rating = rating, food_rating= food_rating, service_rating=service_rating, total_rating= total_rating )
        Restaurent.save(restaurant)
        return JsonResponse({'status': 'success', 'message': 'Ratings submitted successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
   # return render(request,'myapp/addrating.html')


def logout_view(request):
    logout(request)
    response = HttpResponse("You have been logged out.")
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'  # Prevent caching
    response['Pragma'] = 'no-cache'  # Prevent caching in older browsers
    response['Expires'] = '0'
    return redirect('/login')

