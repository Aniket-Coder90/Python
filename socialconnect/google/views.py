from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from socialconnect import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generator_token
from django.core.mail import EmailMessage, send_mail

# Create your views here.
def home(request):
    return render(request, 'google/index.html')

def signup(request):
    
    if request.method == "POST":
        # username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['pass']
        cpassword = request.POST['cpass']
        
        if User.objects.filter(username=username):
            messages.error(request, "This username is not availble")
            return redirect('/signup')
            
        # if User.objects.filter(email=email):
        #     messages.error(request, "This email id already exist.")
        #     return redirect('/signup')
        
        if len(username) > 10:
            messages.error(request, "Please Enter username less than 10 numbers")
            return redirect('/signup')
            
        if password !=  cpassword:
            messages.error(request, "Please Enter Same Password which you entered first")
            return redirect('/signup')
            
        if not username.isalnum():
            messages.error(request, "User name should be Alphanumeric only")
            return redirect('/signup')
            
        myuser = User.objects.create_user(username, email, password)
        myuser.first_name = fname
        myuser.last_name = lname
        # User is not activate directly we are generating token for active and send link to user for that token.py file
        myuser.is_active = False
        myuser.save()
    
        messages.success(request, "Your Account has been successfully created. we have sent you a confirmation email, please confirm and activate your account.")
        
        
        # Welcome Email
        subject = "Welcome to Google Login Page"
        message = "Hello" + myuser.first_name + "!! \n" + "Welcome to Google!!! \n Thank you for visiting \n we have also sent you a confirmation email, please confirm email address in order to activate your account. \n\n Thank you \n Aniket Prajapati"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently = True)
        
        # Email Address confirmation email
        
        current_site = get_current_site(request)
        email_subject = "Confirm your email"
        message2 = render_to_string('email_confirmation.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generator_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email]
        )
        email.fail_silently = True
        email.send()
        
        return redirect('signin')
    
    return render(request, 'google/signup.html')

def signin(request):
    print('This is login pages')
    if request.method == "POST":
        
        username = request.POST['username']
        password = request.POST['pass']
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            username = user.username
            fname = user.first_name
            messages.success(request, "Welcome You are successfully logged in")
            contenxt = {
                'username': username,
                'fname': fname
            }
            print('Verified user')
            
            return render(request, 'google/index.html', contenxt)
            
        else:
            messages.error(request, "Please enter right credentials")
            print('not verified')
            return redirect('/signin')
    
    return render(request, 'google/signin.html')

def signout(request):
    # return render(request, 'google/signout.html')
    logout(request)
    messages.success(request, "You are successfully logged out")
    return redirect('/')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
        
    if myuser is not None and generator_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('/')
    else:
        return render(request, 'google/activation_faild.html')
        