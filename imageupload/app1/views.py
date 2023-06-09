from django.shortcuts import render, redirect
from .forms import ImageForm
from .models import Image
from django.contrib.auth.models import User
# Create your views here.
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from imageupload import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.core.mail import EmailMessage,send_mail
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str



def home(request):
    return render(request, 'app1/home.html')

def signup(request):
    if request.method=="POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            msg = "Username is alrady present, Please try with differnt Username"
            return render(request, 'app1/signup.html',{'msg':msg})

        if User.objects.filter(email=email):
            emailmsg = "email is alrady present, Please try with differnt email"
            return render(request, 'app1/signup.html',{'emailmsg':emailmsg})
        
        if len(username)>10:
            lenmsg = "Username must be under 10 character"
            return render(request, 'app1/signup.html',{'lenmsg':lenmsg})


        myuser = User.objects.create_user(username, email, pass1)
        myuser.is_patient = True

        myuser.first_name = fname
        myuser.last_name = lname

        myuser.is_active = False
        myuser.save()


        ## Welcome Email

        subject = "Welcome To Image Upload Potal !!"
        message = "Hello " + myuser.first_name +  "  !! \n" + "Welcome to Image Upload portal \nThank you for visiting our website \nWe have also sent you a confirmation email, Please confirm your email address in order to activate your account. \n\nThanking you\n Swapnil Kansara"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject,message,from_email, to_list, fail_silently = True)

        ## Confirmation Email

        current_site = get_current_site(request)
        email_subject = "Confirm your email @ Image Upload Portal"
        message2 = render_to_string('email_confirmation.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],

        )
        email.fail_silently = True
        email.send()



        return redirect('signin')
    return render(request, 'app1/signup.html')

def signin(request):
    if request.method == 'POST' :
        username = request. POST['username']
        pass1= request. POST['pass1']
        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return redirect('image_upload',fname=fname)


        else:
            messages.error(request, "Bad Credentioal ")
            return redirect('signin')
    return render(request, 'app1/signin.html')


def signout(request):
    logout(request)
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')


def image_upload(request,fname=None):
    user = request.user
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('image_upload', fname=fname) # redirect to the same view after successful form submission
    else:
        form = ImageForm()
    image = Image.objects.filter(user=user)
    return render(request, 'app1/image_upload.html', {'image':image,'form': form,'fname': fname})