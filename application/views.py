from django.http import HttpResponse, JsonResponse

# Create your views here.
def index(request):
    # return a json response
    return JsonResponse({'message': 'Hello, World!'})
