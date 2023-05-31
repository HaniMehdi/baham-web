import base64
import json
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse, QueryDict
from django.template import loader
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.models import User
from django.db.models import Q
from django.middleware.csrf import get_token

from baham.enum_types import VehicleStatus, VehicleType
from baham.models import Vehicle, VehicleModel, validate_colour, UserProfile


# Create your views here.
def render_login(request, message=None):
    template = loader.get_template('login.html')
    context = {
        'message': message
    }
    return HttpResponse(template.render(context, request))


def view_home(request):
    if not request.user.is_authenticated:
        return render_login(request)
    template = loader.get_template('home.html')
    context = {
        'navbar': 'home',
        'is_superuser': request.user.is_superuser,
    }
    return HttpResponse(template.render(context, request))


def login(request):
    _username = request.POST.get("username")
    _username = _username.lower()
    _password = request.POST.get("password")
    user = User.objects.filter(Q(username=_username) | Q(email=_username)).first()
    if not user:
        return render_login(request, message='User not found. Please check the username/email.')
    if user.check_password(_password):
        auth.login(request, user)
        return HttpResponseRedirect(reverse('home'))
    return render_login(request, message='Invalid password!')


def logout(request):
    auth.logout(request)
    return render_login(request, message='Invalid password!')


def view_aboutus(request):
    template = loader.get_template('aboutus.html')
    context = {
        'navbar': 'aboutus',
        'is_superuser': request.user.is_superuser,
    }
    return HttpResponse(template.render(context, request))


def view_vehicles(request):
    limit = 20
    template = loader.get_template('vehicles.html')
    vehicles = Vehicle.objects.filter(Q(voided=0) & Q(status=VehicleStatus.AVAILABLE.name)).order_by('-date_created')[:limit]
    context = {
        'navbar': 'vehicles',
        'is_superuser': request.user.is_superuser,
        'vehicles': vehicles
    }
    return HttpResponse(template.render(context, request))


def render_create_vehicle(request, message=None):
    template = loader.get_template('createvehicle.html')
    models = VehicleModel.objects.filter(voided=0).order_by('vendor')
    context = {
        'navbar': 'vehicles',
        'is_superuser': request.user.is_superuser,
        'models': models,
        'vehicle_types': [(t.name, t.value) for t in VehicleType],
        'vehicle_statuses': [(t.name, t.value) for t in VehicleStatus],
        'message': message
    }
    return HttpResponse(template.render(context, request))


def create_vehicle(request):
    return render_create_vehicle(request)


def save_vehicle(request):
    _registration_number = request.POST.get('registration_number')
    exists = Vehicle.objects.filter(registration_number=_registration_number)
    if exists:
        return render_create_vehicle(request, message="Another vehicle with this registration number already exists.")
    _model_uuid = request.POST.get('model_uuid')
    _model = VehicleModel.objects.filter(uuid=_model_uuid).first()
    if not _model:
        return render_create_vehicle(request, message="Selected Vehicle model not found! Please select from given list only.")
    _colour = request.POST.get('colour')
    if not validate_colour(_colour):
        return render_create_vehicle(request, message="Invalid colour code!")    
    _status = request.POST.get('status')
    print (_status)
    _picture1 = request.FILES.get('image1')
    _picture2 = request.FILES.get('image2')
    vehicle = Vehicle.objects.create(registration_number=_registration_number, colour=_colour, model=_model, 
                                     owner=request.user, status=_status, picture1=_picture1, picture2=_picture2)
    vehicle.save()
    return HttpResponseRedirect(reverse('vehicles'))


def delete_vehicle(request, uuid):
    if not request.user.is_staff:
        return HttpResponseBadRequest('You are not authorized for this operation!')
    vehicle_model = VehicleModel.objects.filter(uuid=uuid).first()
    if not vehicle_model:
        return HttpResponseBadRequest('This object does not exit!')
    vehicle_model.delete()
    return HttpResponseRedirect(reverse('vehicles'))


def edit_vehicle(request, uuid):
    template = loader.get_template('editvehicle.html')
    vehicle_model = VehicleModel.objects.filter(uuid=uuid).first()
    if not vehicle_model:
        return HttpResponseBadRequest('This object does not exit!')
    context = {
        'navbar': 'vehicles',
        'is_superuser': request.user.is_superuser,
        'vehicle_types': [(t.name, t.value) for t in VehicleType],
        'vehicle': vehicle_model
    }
    return HttpResponse(template.render(context, request))


def update_vehicle(request):
    _uuid = request.POST.get('uuid')
    _vendor = request.POST.get('vendor')
    _model = request.POST.get('model')
    _type = request.POST.get('type')
    _capacity = int(request.POST.get('capacity'))
    if not _vendor or not _model:
        return HttpResponseBadRequest('Manufacturer and Model name fields are mandatory!')
    if not _capacity or _capacity < 2:
        _capacity = 2 if _type == VehicleType.MOTORCYCLE else 4
    vehicle_model = VehicleModel.objects.filter(uuid=_uuid).first()
    if not vehicle_model:
        return HttpResponseBadRequest('Requested object does not exist!')
    vehicle_model.vendor = _vendor
    vehicle_model.model = _model
    vehicle_model.type = _type
    vehicle_model.capacity = _capacity
    vehicle_model.update(update_by=request.user)
    return HttpResponseRedirect(reverse('vehicles'))

#############
### REST ####
#############
def basic_auth(request):
    auth_header = request.META['HTTP_AUTHORIZATION']
    _, encoded_credentials = auth_header.split(' ')
    credentials = base64.b64decode(encoded_credentials).decode('utf-8')
    username, password = credentials.split(':')
    user = User.objects.filter(username=username).first()
    if not user:
        return JsonResponse({'error' : 'User Does Not Exist'}, status=401)
    return user.check_password(password)


def get_csrf_token(request):
    if not (basic_auth(request)):
        return JsonResponse({'error': 'Password Does Not Match'}, status=401)
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token' : csrf_token})
    


def get_all_vehicle_models(request):
    if not (basic_auth(request)):
        return JsonResponse({'error': 'Password Does Not Match'}, status=401)
    if request.method == 'GET':
        vehicle_models = VehicleModel.objects.all()
        data = []
        for model in vehicle_models:
            data.append({
                'uuid': model.uuid,
                'vendor': model.vendor,
                'model': model.model,
                'type': model.type,
                'date_created': model.date_created,
                'created_by': str(model.created_by),
            })
        return JsonResponse({'results': data})
    else:
        return JsonResponse({'error': 'Invalid endpoint or method type'}, status=400)


def get_vehicle_model(request, uuid):
    if request.method == 'GET':
        model = VehicleModel.objects.filter(uuid=uuid).first()
        data = {
            'uuid': model.uuid,
            'vendor': model.vendor,
            'model': model.model,
            'type': model.type,
            'capacity': model.capacity,
            'date_created': model.date_created,
            'created_by': str(model.created_by),
            'date_updated': model.date_updated,
            'updated_by': str(model.updated_by),
            'voided': model.voided,
            'date_voided': model.date_voided,
            'voided_by': str(model.voided_by),
            'void_reason': model.void_reason,
        }
        return JsonResponse({'results': data})
    else:
        return JsonResponse({'error': 'Invalid endpoint or method type'}, status=400)


def create_vehicle_model(request):
    if request.method == 'POST':
        _vendor = request.POST.get('vendor')
        _model = request.POST.get('model')
        _type = request.POST.get('type')
        _capacity = request.POST.get('capacity')
        vehicle_model = VehicleModel.objects.create(vendor=_vendor, model=_model, type=_type, capacity=_capacity)
        response_data = {
            'message': 'Vehicle model created successfully',
            'uuid': vehicle_model.uuid,
        }
        return JsonResponse(response_data, status=201)
    else:
        return JsonResponse({'error': 'Invalid endpoint or method type'}, status=400)


def update_vehicle_model(request, uuid):
    if request.method == 'PUT':
        params = QueryDict(request.body)
        _vendor = params.get('vendor')
        _model = params.get('model')
        _type = params.get('type')
        _capacity = params.get('capacity')
        vehicle_model = VehicleModel.objects.filter(uuid=uuid).first()
        if not vehicle_model:
            response_data = {
                'error': 'Vehicle model not found',
            }
            return JsonResponse(response_data, status=404)
        vehicle_model.vendor = _vendor
        vehicle_model.model = _model
        vehicle_model.type = _type
        vehicle_model.capacity = _capacity
        vehicle_model.update()
        response_data = {
            'message': 'Vehicle model updated successfully',
            'uuid': vehicle_model.uuid,
        }
        return JsonResponse(response_data, status=200)
    else:
        return JsonResponse({'error': 'Invalid endpoint or method type'}, status=400)


def delete_vehicle_model(request, uuid):
    if request.method == 'DELETE':
        vehicle_model = VehicleModel.objects.filter(uuid=uuid).first()
        if not vehicle_model:
            response_data = {
                'error': 'Vehicle model not found',
            }
            return JsonResponse(response_data, status=404)
        vehicle_model.delete()
        response_data = {
            'message': 'Vehicle model voided successfully'
        }
        return JsonResponse(response_data, status=200)
    else:
        return JsonResponse({'error': 'Invalid endpoint or method type'}, status=400)
    

def get_all_user_profiles(request):
    if not (basic_auth(request)):
        return JsonResponse({'error': 'Password Does Not Match'}, status=401)
    if request.method == 'GET':
        user_profiles = UserProfile.objects.all()
        data = []
        for user in user_profiles:
            data.append({
                'uuid': user.uuid,
                'username': user.user.username,
                'email': user.user.email,
                'birthdate': user.birthdate,
                'gender': user.gender,
                'type': user.type,
                'primary_contact': user.primary_contact,
                'alternate_contact': user.alternate_contact,
                'address' : user.address,
                'landmark': user.landmark,
                'town': user.town,
                'bio': user.bio        
            })
        return JsonResponse({'results': data})
    else:
        return JsonResponse({'error': 'Invalid endpoint or method type'}, status=400)
    

def get_user_profile(request, uuid):
    if not (basic_auth(request)):
        return JsonResponse({'error': 'Password Does Not Match'}, status=401)
    if request.method == 'GET':
        user = UserProfile.objects.filter(uuid=uuid).first()
        data = {
            'uuid': user.uuid,
                'username': user.user.username,
                'email': user.user.email,
                'birthdate': user.birthdate,
                'gender': user.gender,
                'type': user.type,
                'primary_contact': user.primary_contact,
                'alternate_contact': user.alternate_contact,
                'address' : user.address,
                'landmark': user.landmark,
                'town': user.town,
                'bio': user.bio     
        }
        return JsonResponse({'results': data})
    else:
        return JsonResponse({'error': 'Invalid endpoint or method type'}, status=400)
    

def create_user_profile(request):
    if not (basic_auth(request)):
        return JsonResponse({'error': 'Password Does Not Match'}, status=401)
    if request.method == 'POST':
        _username = request.POST.get('username')
        _email = request.POST.get('email')
        _password = request.POST.get('password')
        _repassword = request.POST.get('repassword')
        if _username is None:
            return JsonResponse({'error': 'Username Is Required'}, status=400)
        user = User.objects.filter(username=_username).first()
        if user is not None:
            return JsonResponse({'error': 'Username Is Already Taken'}, status=400)
        if _email is None:
            return JsonResponse({'error': 'Email Is Required'}, status=400)
        if _password is None or _repassword is None:
            return JsonResponse({'error': 'Both Passwords Are Required'}, status=400)
        if _password != _repassword:
            return JsonResponse({'error': 'Both Passwords Do Not Match'}, status=400)
        user = User.objects.create_superuser(username=_username, email=_email, password=_password)
        _birthdate = request.POST.get('birthdate')
        _gender = request.POST.get('gender')
        _type = request.POST.get('type')
        _primary_contact = request.POST.get('primary_contact')
        _alternate_contact = request.POST.get('alternate_contact')
        _address = request.POST.get('address')
        _address_latitude = request.POST.get('address_latitude')
        _address_longitude = request.POST.get('address_longitude')
        _landmark = request.POST.get('landmark')
        _town = request.POST.get('town')
        _bio = request.POST.get('bio')
        user_profile = UserProfile.objects.create(user=user, birthdate=_birthdate, gender=_gender, type=_type, primary_contact=_primary_contact,
                                                 alternate_contact=_alternate_contact, address=_address, address_latitude=_address_latitude,
                                                 address_longitude=_address_longitude, landmark=_landmark, town=_town, bio=_bio)
        response_data = {
            'message': 'User Profile created successfully',
            'uuid': user_profile.uuid,
        }
        return JsonResponse(response_data, status=201)
    else:
        return JsonResponse({'error': 'Invalid endpoint or method type'}, status=400)
    

def update_user_profile(request, uuid):
    if not (basic_auth(request)):
        return JsonResponse({'error': 'Password Does Not Match'}, status=401)
    if request.method == 'PUT':
        params = QueryDict(request.body)
        _birthdate = params.get('birthdate')
        _gender = params.get('gender')
        _type = params.get('type')
        _primary_contact = params.get('primary_contact')
        _alternate_contact = params.get('alternate_contact')
        _address = params.get('address')
        _address_latitude = params.get('address_latitude')
        _address_longitude = params.get('address_longitude')
        _landmark = params.get('landmark')
        _town = params.get('town')
        _bio = params.get('bio')
        user_profile = UserProfile.objects.filter(uuid=uuid).first()
        if not user_profile:
            response_data = {
                'error': 'User Profile not found',
            }
            return JsonResponse(response_data, status=404)
        user_profile.birthdate = _birthdate
        user_profile.gender = _gender
        user_profile.type = _type
        user_profile.primary_contact = _primary_contact
        user_profile.alternate_contact = _alternate_contact
        user_profile.address = _address
        user_profile.address_latitude = _address_latitude
        user_profile.address_longitude = _address_longitude
        user_profile.landmark = _landmark
        user_profile.town = _town
        user_profile.bio = _bio
        user_profile.update()
        response_data = {
            'message': 'User Profile updated successfully',
            'uuid': user_profile.uuid,
        }
        return JsonResponse(response_data, status=200)
    else:
        return JsonResponse({'error': 'Invalid endpoint or method type'}, status=400)
    

def delete_user_profile(request, uuid):
    if not (basic_auth(request)):
        return JsonResponse({'error': 'Password Does Not Match'}, status=401)
    if request.method == 'DELETE':
        user_profile = UserProfile.objects.filter(uuid=uuid).first()
        if not user_profile:
            response_data = {
                'error': 'User Profile not found',
            }
            return JsonResponse(response_data, status=404)
        user_profile.delete()
        response_data = {
            'message': 'User Profile voided successfully'
        }
        return JsonResponse(response_data, status=200)
    else:
        return JsonResponse({'error': 'Invalid endpoint or method type'}, status=400)
    
