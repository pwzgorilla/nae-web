from django.http import HttpResponse
from django.shortcuts import render_to_response
import requests
from auth.decorators import require_auth
from django.http import HttpResponseRedirect
import json
from jaeweb.settings import BASE_URL


# Create your views here.

@require_auth
def index(request):
    project_id = request.GET.get('project_id')
    user_id = request.GET.get('user_id')
    url="{}/containers?project_id={}&user_id={}".format(BASE_URL,project_id,user_id)
    headers={'Content-Type':'application/json'}
    rs = requests.get(url,headers=headers)
    container_list_org = rs.json()
    #for container in container_list:
    #    image_id = container.pop('image_id',None)
    #    image = ""
    #    if image_id: 
    #        url='{}/images/{}'.format(BASE_URL,image_id)
    #        headers={'Content-Type':'application/json'}
    #        resp = requests.get(url,headers=headers)
    #        try:
    #            image = "%s:%s" % (resp.json()['name'],resp.json()['tag'])
    #        except KeyError as ex:
    #            raise
    #    container.update({"image":image})
    #    container_list.append(container)
    container_list = []
    for container in container_list_org:
        repos = container.pop("repos",None)
        if repos is not None:
            repos = repos.split("/")[-1] 
        container.update({"repos":repos})
        container_list.append(container)

    """get current user role in current project."""
    url='%s/projects/%s' % (BASE_URL,project_id)
    headers={'Content-Type':'application/json'}
    rs = requests.get(url,headers=headers)
    users = rs.json()['users'] 
    project_role=None
    for user in users:
        if user['name'] == user_id:
            project_role = user['role_id']

    print 'project_role',project_role
   
    return render_to_response('container-table-replace.html',
                             {'container_list':container_list,
                              'project_role': project_role})

@require_auth
def detail(request):
    #project_id=os.path.basename(request.path)
    container_id=request.GET['id']
    url='{}/containers/{}'.format(BASE_URL,container_id)
    headers={'Content-Type':'application/json'}
    rs = requests.get(url,headers=headers)
    container_info = rs.json()
    return render_to_response('container_info.html',{'container_info':container_info})


@require_auth
def create(request):
    if request.method == 'POST':
        container_environ = request.POST.get('container_env') 
        container_project = request.POST.get('project_id')
        container_image   = request.POST.get('image_name')
        repos             = request.POST.get('repos')
        container_code    = request.POST.get('container_code')
        app_type          = request.POST.get('app_type')
        user_name         = request.session.get('user_id')
        user_key          = request.session.get('user_key')
        zone_id           = request.POST.get('zone_id')
        maven_flags       = request.POST.get('maven_flags')

        url='{}/containers'.format(BASE_URL)
        headers={'Content-Type':'application/json'}
        data = {
                'env':container_environ,
                'project_id':container_project,
                'image_id':container_image,
                'repos':repos,
                'branch':container_code,
                'app_type':app_type,
                'user_id':user_name,
                'user_key':user_key,
                'zone_id': zone_id,
                'maven_flags': maven_flags,
        }
        rs = requests.post(url,headers=headers,data=json.dumps(data))
    return HttpResponse(json.dumps(rs.json()))

@require_auth
def delete(request):
    container_id=request.GET['id']
    v=request.GET['v']
    url = '{}/containers/{}?v={}'.format(BASE_URL,container_id,v)
    headers={'Content-Type':'application/json'}
    requests.delete(url,headers=headers)
    return HttpResponse("succeed")

@require_auth
def update(request):
    project_id = request.GET.get('project_id')
    user_id = request.GET.get('user_id')
    url='{}/containers?project_id={}&user_id={}'.format(BASE_URL,project_id,user_id)
    headers={'Content-Type':'application/json'}
    rs = requests.get(url,headers=headers)
    container_list_org = rs.json()

    container_list = []
    for container in container_list_org:
        repos = container.pop("repos",None)
        if repos is not None:
            repos = repos.split("/")[-1] 
        container.update({"repos":repos})
        container_list.append(container)

    print container_list
    """get current user role in current project."""
    url='%s/projects/%s' % (BASE_URL,project_id)
    headers={'Content-Type':'application/json'}
    rs = requests.get(url,headers=headers)

    project_info = rs.json()
    user_id = request.session.get('user_id',None)

    """get current user role in project"""
    project_role = None 
    if project_info:
        for user in project_info['users']:
            if user['name'] == user_id:
                project_role=user['role_id']

    if request.session.get('user_role',None) == 'admin':
        role=0
    elif project_role == 0:
        role=0
    else:
        role=project_role

    print role
    return render_to_response('container-table-replace.html',
                             {'container_list':container_list,
                              'role': role})

@require_auth
def stop(request):
    ctn_id = request.GET['id']
    url = '{}/containers/{}/stop'.format(BASE_URL,ctn_id)
    headers={'Content-Type':'application/json'}
    requests.post(url,headers=headers)
    return HttpResponse("succeed")

@require_auth
def start(request):
    ctn_id = request.GET['id']
    url = '{}/containers/{}/start'.format(BASE_URL,ctn_id)
    headers={'Content-Type':'application/json'}
    requests.post(url,headers=headers)
    return HttpResponse("succeed")

@require_auth
def reboot(request):
    ctn_id = request.GET['id']
    url = '{}/containers/{}/reboot'.format(BASE_URL,ctn_id)
    headers={'Content-Type':'application/json'}
    requests.post(url,headers=headers)
    return HttpResponse("succeed")

@require_auth
def commit(request):
    ctn_id = request.GET['id']
    url = '{}/containers/{}/commit'.format(BASE_URL,ctn_id)
    headers={'Content-Type':'application/json'}
    requests.post(url,headers=headers)
    return HttpResponse("succeed")

@require_auth
def destroy(request):
    ctn_nm = request.GET.get('name')
    url = '{}/containers/{}/destroy'.format(BASE_URL,ctn_nm)
    headers={'Content-Type':'application/json'}
    requests.post(url,headers=headers)
    return HttpResponse("succeed")

@require_auth
def refresh(request):
    id = request.GET.get('id')
    branch = request.GET.get('branch')
    url = '%s/containers/%s/refresh?branch=%s' % ( BASE_URL,id,branch)
    headers = {'Content-Type':'application/json'}
    requests.get(url,headers=headers)
    return HttpResponse("succeed") 

from jaeweb.settings import app_key, app_name, auth_key, auth_url

@require_auth
def share(request):
    id = request.GET.get('id')
    user_id = request.GET.get('user_id')
    user_name = request.GET.get('user_name')

    url = "%s%s%s%s%s" % (auth_url, "/api/allkey/?",app_key, auth_key, app_name)
    headers = {'content-type': 'application/json'}
    auth_result = requests.get(url, headers=headers,)
    for item in auth_result.json():
        if item['uid'] == user_name: 
            user_key = item['key']

    data = {'user_id': user_name, 'user_key': user_key}
    #url = "%s/containers/%s/share?user_id=%s&user_key=%s" % (BASE_URL, id, user_name, user_key)
    url = "%s/containers/%s/share" % (BASE_URL, id)
    headers = {'Content-Type':'application/json'}
    requests.post(url,headers=headers,data=json.dumps(data))
    return HttpResponse("succeed") 
