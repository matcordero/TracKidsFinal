import io
from pathlib import Path
import select
import shutil
import subprocess as sp
import sys
from typing import Dict, Tuple, Optional, IO
import os
import uuid
from django.http import JsonResponse, FileResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from pytube import YouTube
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password, check_password
# Create your views here.
import cloudinary.uploader
import demucs.separate

from AppTracKids.models import Songs, Usuario, Project

# Token
def validarToken(request):
    authorization_header = request.headers.get('Authorization')
    if authorization_header:
        print("--------------------")
        print(authorization_header)
        print("--------------------")
        token = authorization_header.split(' ')[1]
    else:
        return None  # Retorna None si no hay token en el header
    try:
        usuario_actual = Usuario.objects.get(keyValidate=token)
        return usuario_actual
    except Usuario.DoesNotExist:
        return None  # Retorna None si no se encuentra el usuario

# Metodos de Usuario
@csrf_exempt
@api_view(['POST'])
def register(request):
    #User = get_user_model()
    email = request.data.get('email')
    password = request.data.get('password')
    name = request.data.get('name')
    
    if not all([email, password, name]):
        return JsonResponse({"error": "Campos Vacios"}, status=400)

    if Usuario.objects.filter(email=email).exists():
        return JsonResponse({"error": "El Usuario ya existe"}, status=400)

    contrasena_encriptada = make_password(password)
    usuario = Usuario(email=email, name=name, password=contrasena_encriptada)
    usuario.save()

    return JsonResponse({"message": "Usuario Creado con Éxito"}, status=201)

@csrf_exempt
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')
    #obtener_usuarios()
    try:
        user = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        user = None
    if user is not None and check_password(password, user.password):
        # and user.contraseña == make_password(contrasena)
        keyValidate = str(uuid.uuid4()).replace("-", "")
        user.keyValidate = keyValidate
        user.save()
        response_data = {
            'nombre': user.name,
            'keyValidate': keyValidate,
            'icon': user.icon,
        }
        return JsonResponse(response_data, status=202)
    else:
        response_data = {
            'error': 'Usuario o Contraseña Incorrecto'
        }
        return JsonResponse(response_data, status=400)

@csrf_exempt
@api_view(['GET'])
def getUsuario(request):
    usuario_actual = validarToken(request)
    if usuario_actual:
        response_data = {
            'name': usuario_actual.name,
            'birtDate': usuario_actual.birtDate,
            'email': usuario_actual.email,
            'icon': usuario_actual.icon
        }
        return JsonResponse(response_data, status=200)
    else:
        return JsonResponse({'error': 'Fallo de Validacion'}, status=400)

@csrf_exempt
@api_view(['GET'])
def getProyectos(request):
    #Buscar Usuario
    usuario_actual = validarToken(request)
    if usuario_actual==None:
        return JsonResponse({'error': 'Fallo de Validacion'}, status=400)
    proyectos = Project.objects.filter(usuario=usuario_actual)
    proyectosResponse = []
    for proyecto in proyectos:
        proyectoData = {
            'id': proyecto.id,
            'tittle': proyecto.titulo,
            'imagen': proyecto.imagen,
            'vocals': proyecto.vocals,
            'other': proyecto.other,
            'drums': proyecto.drums,
            'bass': proyecto.bass
        }
        proyectosResponse.append(proyectoData)
    return JsonResponse(proyectosResponse, status=200, safe=False)

# Metodos de Separacion de Pistas | Proyectos
@csrf_exempt
@api_view(['GET'])
def getAllProyectos(request):
    #Buscar Usuario
    proyectos = Project.objects.all()
    proyectosResponse = []
    for proyecto in proyectos:
        proyectoData = {
            'id': proyecto.id,
            'tittle': proyecto.titulo,
            'imagen': proyecto.imagen,
            'vocals': proyecto.vocals,
            'other': proyecto.other,
            'drums': proyecto.drums,
            'bass': proyecto.bass
        }
        proyectosResponse.append(proyectoData)
    return JsonResponse(proyectosResponse, status=200, safe=False)

@csrf_exempt
@api_view(['GET'])
def getAllSongs(request):
    #Buscar Usuario
    canciones = Songs.objects.all()
    cancionesResponse = []
    for cancion in canciones:
        cancionData = {
            'id': cancion.id,
            'tittle': cancion.titulo,
            'info':cancion.info,
            'artist': cancion.artista,
            'cover': cancion.imagen,
            'vocals': cancion.vocals,
            'other': cancion.other,
            'drums': cancion.drums,
            'bass': cancion.bass,
            'track':cancion.track
        }
        cancionesResponse.append(cancionData)
    return JsonResponse(cancionesResponse, status=200, safe=False)

@csrf_exempt
@api_view(['GET'])
def getOneSong(request):
    # Obtener la primera canción
    cancion = Songs.objects.last()

    # Verificar si se encontró una canción
    if cancion:
        cancionData = {
            'id': cancion.id,
            'tittle': cancion.titulo,
            'info': cancion.info,
            'artist': cancion.artista,
            'cover': cancion.imagen,
            'vocals': cancion.vocals,
            'other': cancion.other,
            'drums': cancion.drums,
            'bass': cancion.bass,
            'track':cancion.track
        }
        return JsonResponse(cancionData, status=200)
    else:
        return JsonResponse({'message': 'No se encontraron canciones'})

@csrf_exempt
@api_view(['POST'])
def proyectoToSong(request):
    id = request.data.get('id')
    info = request.data.get('info')
    artist = request.data.get('artista')
    
    proyecto = Project.objects.get(id=id)
    if proyecto == None:
        return JsonResponse({'error': 'Proyecto no Encontrado'}, status=404)
    
    
    cancion = Songs(
        info = info,
        artista = artist,
        titulo=proyecto.titulo,
        imagen=proyecto.imagen,
        vocals=proyecto.vocals,
        other=proyecto.other,
        drums=proyecto.drums,
        bass=proyecto.bass
        )   
    cancion.save()
    
    
    return JsonResponse({"message":"Guardado"}, status=201)

@csrf_exempt
@api_view(['POST'])
def cancionSemanaYoutube(request):
       
    #Datos Solicitados
    link = request.data.get('link')
    info = request.data.get('info')
    artist = request.data.get('artista') 
    #Cargar Video
    video = YouTube(link)
    nombre = video.title
    directorio = os.getcwd()+f"/{nombre}/demucs/"
    mp3_file = f"{nombre}.mp3"
    # Descargar solo el audio
    audio_stream = video.streams.filter(only_audio=True).first()
    audio_stream.download(output_path=directorio, filename=mp3_file)
    
    Salida = separarPistas(nombre)
    if Salida == False:
        return JsonResponse({"error": "Fallo en la separacion"}, status=500)
    urls = cargarPistasCloudinary(nombre)
    urlTrack = cargarCancionCompleta(nombre)
    borrarResultados(nombre)
    cancion = Songs(
        info = info,
        artista = artist,
        titulo=nombre,
        imagen=video.thumbnail_url,
        track = urlTrack,
        vocals=urls["vocals"],
        other=urls["other"],
        drums=urls["drums"],
        bass=urls["bass"]
        )   
    cancion.save()
    
    return JsonResponse({"message":"Guardado"}, status=201)


def validarProyecto(id):
    try:
        proyectoActual = Project.objects.get(id=id)
        return proyectoActual
    except Project.DoesNotExist:
        return None

@csrf_exempt
@api_view(['POST'])
def obtenerSeparacionPorYoutube(request):
    #Buscar Usuario
    usuario_actual = validarToken(request)
    if usuario_actual==None:
        return JsonResponse({'error': 'Fallo de Validacion'}, status=400)
    
    #Datos Solicitados
    link = request.data.get('link')
    
    #Cargar Video
    video = YouTube(link)
    nombre = video.title
    directorio = os.getcwd()+f"/{nombre}/demucs/"
    mp3_file = f"{nombre}.mp3"
    # Descargar solo el audio
    audio_stream = video.streams.filter(only_audio=True).first()
    audio_stream.download(output_path=directorio, filename=mp3_file)
    
    Salida = separarPistas(nombre)
    if Salida == False:
        return JsonResponse({"error": "Fallo en la separacion"}, status=500)
    urls = cargarPistasCloudinary(nombre)
    borrarResultados(nombre)
    proyecto = Project(
        usuario=usuario_actual,
        titulo=nombre,
        imagen=video.thumbnail_url,
        vocals=urls["vocals"],
        other=urls["other"],
        drums=urls["drums"],
        bass=urls["bass"]
        )   
    proyecto.save()
    
    response = {
        'id': proyecto.id,
        'tittle': nombre,
        'imagen': proyecto.imagen,
        'vocals': urls['vocals'],
        'other': urls['other'],
        'drums': urls['drums'],
        'bass': urls['bass']
    }
    return JsonResponse(response, status=201)
    
@csrf_exempt
@api_view(['POST'])
def obtenerSeparacionPorAudio(request):
    #Buscar Usuario
    usuario_actual = validarToken(request)
    if usuario_actual==None:
        return JsonResponse({'error': 'Fallo de Validacion'}, status=400)
    
    #Datos Solicitados
    audio = request.FILES.get('audio')
    nombre = request.data.get('tittle')
    imagen = request.FILES.get('imagen')
    nombre = nombre.replace(" ", "")
    #Cargar Imagen a Cloudinary
    cloudinary_response = cloudinary.uploader.upload(imagen)
    imagen_url = cloudinary_response.get("url")

    #Guardar Video
    directorio = os.getcwd()+f"/{nombre}/demucs/"
    nombreAudio = nombre
    if not nombreAudio.endswith(".mp3"):
        nombreAudio += ".mp3"

    # Crear un sistema de almacenamiento
    fs = FileSystemStorage(location=directorio)

    # Guardar el archivo con el nombre especificado
    fs.save(nombreAudio, audio)

    #Separar las Pistas
    Salida = separarPistas(nombre)
    if Salida == False:
        return JsonResponse({"error": "Fallo en la separacion"}, status=500)
    urls = cargarPistasCloudinary(nombre)
    borrarResultados(nombre)
    proyecto = Project(
        usuario=usuario_actual,
        titulo=nombre,
        imagen=imagen_url,
        vocals=urls["vocals"],
        other=urls["other"],
        drums=urls["drums"],
        bass=urls["bass"]
        )   
    proyecto.save()
    
    response = {
        'id': proyecto.id,
        'tittle': nombre,
        'imagen': proyecto.imagen,
        'vocals': urls['vocals'],
        'other': urls['other'],
        'drums': urls['drums'],
        'bass': urls['bass']
    }
    return JsonResponse(response, status=201)

@csrf_exempt
@api_view(['PUT'])
def modificarProyecto(request):
    #Datos Solicitados
    id = request.data.get('id')
    vocals = request.FILES.get('vocals')
    other = request.FILES.get('other')
    drums = request.FILES.get('drums')
    bass = request.FILES.get('bass')
    
    usuario_actual = validarToken(request)
    if usuario_actual==None:
        return JsonResponse({'error': 'Fallo de Validacion'}, status=400)
    
    proyectoActual = validarProyecto(id)
    if proyectoActual==None:
        return JsonResponse({'error': 'Proyecto no Encontrado'}, status=404)
    
    #Guardar Video
    carpeta = "modificado"
    directorio = os.getcwd()+f"\\{carpeta}\\demucs_separated\\htdemucs\\{carpeta}"
    # Crear un sistema de almacenamiento
    fs = FileSystemStorage(location=directorio)

    # Guardar el archivo con el nombre especificado
    fs.save("vocals.mp3", vocals)
    fs.save("other.mp3", other)
    fs.save("drums.mp3", drums)
    fs.save("bass.mp3", bass)
    
    urls = cargarPistasCloudinary(carpeta)
    
    proyectoActual.vocals=urls["vocals"]
    proyectoActual.other=urls["other"]
    proyectoActual.drums=urls["drums"]
    proyectoActual.bass=urls["bass"]
    proyectoActual.save()
    
    borrarResultados(carpeta)
    
    return JsonResponse({'message': 'Proyecto Modificado'}, status=200)
    
def borrarResultados(nombre):
    carpeta = os.getcwd()+f"/{nombre}/"
    shutil.rmtree(carpeta)
    
def separarPistas(nombre):
    try:
        # Definir las variables necesarias
        model = "htdemucs"
        extensions = ["mp3", "wav", "ogg", "flac"]
        two_stems = None
        mp3 = True
        mp3_rate = 320
        float32 = False
        int24 = False
        # Obtener la ruta del directorio actual
        ruta_actual = os.getcwd()

        # Definir las rutas de entrada y salida
        in_path = ruta_actual + f'/{nombre}/demucs/'
        out_path = ruta_actual + f'/{nombre}/demucs_separated/'

        # Función para encontrar archivos
        def find_files(in_path):
            out = []
            for file in Path(in_path).iterdir():
                if file.suffix.lower().lstrip(".") in extensions:
                    out.append(file)
            return out

        # Función para copiar streams del proceso
        def copy_process_streams(process: sp.Popen):
            def raw(stream: Optional[IO[bytes]]) -> IO[bytes]:
                assert stream is not None
                if isinstance(stream, io.BufferedIOBase):
                    stream = stream.raw
                return stream

            p_stdout, p_stderr = raw(process.stdout), raw(process.stderr)
            stream_by_fd: Dict[int, Tuple[IO[bytes], io.StringIO, IO[str]]] = {
                p_stdout.fileno(): (p_stdout, sys.stdout),
                p_stderr.fileno(): (p_stderr, sys.stderr),
            }
            fds = list(stream_by_fd.keys())

            while fds:
                try:
                    # `select` syscall will wait until one of the file descriptors has content.
                    ready, _, _ = select.select(fds, [], [])
                except select.error:
                    break

                for fd in ready:
                    p_stream, std = stream_by_fd[fd]
                    raw_buf = p_stream.read(2 ** 16)
                    if not raw_buf:
                        fds.remove(fd)
                        continue
                    buf = raw_buf.decode()
                    std.write(buf)
                    std.flush()

        # Función para separar archivos
        def separate(inp=None, outp=None):
            inp = inp or in_path
            outp = outp or out_path
            cmd = ["python", "-m", "demucs.separate", "-o", str(outp), "-n", model]
            if mp3:
                cmd += ["--mp3", f"--mp3-bitrate={mp3_rate}"]
            if float32:
                cmd += ["--float32"]
            if int24:
                cmd += ["--int24"]
            if two_stems is not None:
                cmd += [f"--two-stems={two_stems}"]
            files = [str(f) for f in find_files(inp)]
            if not files:
                return False
            p = sp.Popen(cmd + files, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
            copy_process_streams(p)
            p.wait()
            if p.returncode != 0:
                return False
            return True
        # Llamar a la función separate
        return separate() 
    except Exception as e:
        print(e)
        return False
    
def cargarPistasCloudinary(nombre):
    def obtenerUrl(mp3_path):
        CLOUDINARY = {
            'cloud_name': 'dewiieivf',
            'api_key': '369268768791138',
            'api_secret': '6HucCaibPEhkVm-W3JREtd0eNSo',
        }
        
        cloudinary_response = cloudinary.uploader.upload(mp3_path, resource_type='raw')
        cloudinary_url = cloudinary_response.get('secure_url')
        #print(cloudinary_url)
        return cloudinary_url
    
    carpeta = os.getcwd()+f"\\{nombre}\\demucs_separated\\htdemucs\\{nombre}\\"
    urls = {
        "bass": obtenerUrl(carpeta + "bass.mp3"),
        "drums": obtenerUrl(carpeta + "drums.mp3"),
        "other": obtenerUrl(carpeta + "other.mp3"),
        "vocals": obtenerUrl(carpeta + "vocals.mp3")
    }
    return urls

def cargarCancionCompleta(nombre):
    def obtenerUrl(mp3_path):
        CLOUDINARY = {
            'cloud_name': 'dewiieivf',
            'api_key': '369268768791138',
            'api_secret': '6HucCaibPEhkVm-W3JREtd0eNSo',
        }
        
        cloudinary_response = cloudinary.uploader.upload(mp3_path, resource_type='raw')
        cloudinary_url = cloudinary_response.get('secure_url')
        #print(cloudinary_url)
        return cloudinary_url
    
    carpeta = os.getcwd()+f"/{nombre}/demucs/"
    url = obtenerUrl(carpeta + f"{nombre}.mp3")
    return url
    