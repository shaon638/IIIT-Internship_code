import cv2
import math
import os
import librosa
import soundfile as sf
import subprocess
import platform

def getFps(video_read):
  fps = video_read.get(cv2.CAP_PROP_FPS)
  frame_width = video_read.get(cv2.CAP_PROP_FRAME_WIDTH)
  frame_height = video_read.get(cv2.CAP_PROP_FRAME_HEIGHT)
  total_Frame_Number = int(video_read.get(cv2.CAP_PROP_FRAME_COUNT))
  return fps, frame_width, frame_height, total_Frame_Number

def getFrameNumber(fps, milisecond):
  frame_number = math.floor((fps/1000)*milisecond)
  return frame_number  


def minutes2mili(tm):
  tm_split = tm.split('|')
  tm_mili =(int(tm_split[0])*60000)+(int(tm_split[1])*1000)+int(tm_split[2])
  return tm_mili

def getFrame(video_path,first_time_instant, second_time_instant,path_file):
  basename = os.path.basename(video_path)
  basename = basename.split('.')
  file_name = basename[0]+'_'+'trimmed'+'.'+basename[1]
  print(file_name)
  dirname = path_file
  count =0
  frame_list = []
  first_time_mili = minutes2mili(first_time_instant)
  second_time_mili = minutes2mili(second_time_instant)
  video_cap = cv2.VideoCapture(video_path)

  fps, w, h, f_num = getFps(video_cap)
  total_length_video = (f_num/fps)*1000
  if(first_time_mili < 0):
    print("Sorry time stamp is invalid!!")
    return -1
  elif (second_time_mili > total_length_video):
    print("Sorry time stamp exceeded from the actual video's time stamp !!!")
    print("total timestamp of your video in sec is : ", total_length_video/1000)
    return -1
  else:
      starting_frame = getFrameNumber(fps,first_time_mili)
      ending_frame = getFrameNumber(fps, second_time_mili)
      while(video_cap.isOpened()):
        success, frame = video_cap.read()
        count += 1

        if count >= starting_frame and count <= ending_frame:
          frame_list.append(frame)
          if count == ending_frame:
            break


  videoFile = createVideo(frame_list, fps,int(w),int(h), file_name,dirname)
  return videoFile

def getCropFrame(video_path,a,b,c,d,path_file):
  basename = os.path.basename(video_path)
  basename = basename.split('.')
  file_name = basename[0]+'_'+'cropped'+'.'+basename[1]
  dirname = path_file
  video_cap = cv2.VideoCapture(video_path)
  
  list_frame = []
  count =0
  fps, w, h, f_num = getFps(video_cap)
  
  if (a<0 or b<0):
    print("invalid x1 or y1 coordinate!!")
    print("please put the write coordinate")
    return -1
  elif(c>w):
    print("width of the frame is exceeded!!")
    print("the weidth frame limit will be maximum: ",w)
    return -1

  elif(d>h):
    print("Height of the frame is exceeded!!!")
    print("the height of the frame limit will be maximum: ",h)
    return -1

  elif(a>c):
    print("Sorry invalid coordinate!!")
    return -1

  elif(b>d):
    print("Sorry invalid coordinate!!")
    return -1
  else:
    while(video_cap.isOpened()):
      success, frame = video_cap.read()
      count += 1
      cropped_frame = frame[int(b):int(d) , int(a):int(c)]
      list_frame.append(cropped_frame)
    
      if f_num == count:
        break
  height = list_frame[0].shape[0]
  weidth = list_frame[0].shape[1]
  videoFile = createVideo(list_frame, fps,weidth, height,file_name, dirname)
  return videoFile

def createVideo(list_of_frame, fps, w, h,basename_file,folder_des):
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    saved_file = folder_des+'/'+basename_file
    writer = cv2.VideoWriter(saved_file, fourcc, fps, (w, h))
    
    for i in range (len(list_of_frame)):
      writer.write(list_of_frame[i])
  
    writer.release()
    return saved_file


def getFrameResize(video_path,weight, height,path_file):
  basename = os.path.basename(video_path)
  basename = basename.split('.')
  file_name = basename[0]+'_'+'resized'+'.'+basename[1]
  dirname = path_file
  video_cap = cv2.VideoCapture(video_path)
  list_frame = []
  count= 0
  fps, w, h, f_num = getFps(video_cap)

  if(weight <=0 or height <=0):

    print('weidth or height are invalid!!!')
    return -1
  else:
    while(video_cap.isOpened()):
      success, frame = video_cap.read()
      count += 1
  
      res_frame = cv2.resize(frame, (weight, height), interpolation = cv2.INTER_LINEAR)
      list_frame.append(res_frame)
   
      
      if count == f_num:
        break
  videofile = createVideo(list_frame, fps, weight, height,file_name,dirname)
  return videofile

def getFrameAspect(video_path, weight,path_file):
  basename = os.path.basename(video_path)
  basename = basename.split('.')
  file_name = basename[0]+'_'+'resized'+'.'+basename[1]
  dirname = path_file
  video_cap = cv2.VideoCapture(video_path)
  fps, w, h, f_num = getFps(video_cap)
  height = weight
  lst_fr = []
  count = 0
  if weight == 0:
    print("invalid weidth!!!")
    return -1
  else:

    while (video_cap.isOpened()):
      success, frame = video_cap.read()
      count += 1
      res_frame  =cv2.resize(frame, (weight, height))
      lst_fr.append(res_frame)

      if count == f_num:
        break
  video_file = createVideo(lst_fr, weight, height, file_name,dirname)
  return video_file

def getAudioSampleNum(time, sf):
  milisecond = minutes2mili(time)
  sample_num = math.floor((sf/1000)*milisecond)
  return sample_num

def trimAudio(video_path, starting_time, ending_time,dirname):
  basename = os.path.basename(video_path)
  basename = basename.split('.')
  file_name = basename[0]+'_'+'trimmed'+'.'+'wav'
  path_name = dirname
  audio, sr = librosa.load(video_path, 16000)
  sample_start = getAudioSampleNum(starting_time,sr)
  sample_end = getAudioSampleNum(ending_time,sr)
  trimmed_audio = audio[sample_start: sample_end]
  audioFile = writeAudio(file_name, trimmed_audio, sr, path_name)
  return audioFile

def writeAudio(basename,audio, sr,folder_des):
  saved_file = folder_des+'/'+basename
  sf.write(saved_file,audio, sr)
  return saved_file

def audioMergevideo(video, audio, saved_file):
  basename = os.path.basename(video)
  basename = basename.split('.')
  final_video = saved_file + '/'+basename[0]+'Merged'+'.'+basename[1]
  command = 'ffmpeg -y -i {} -i {} -strict -2 -q:v 1 {}'.format(audio, video, final_video)
  subprocess.call(command, shell=platform.system() != 'Windows')

def getAudio(video_path, path_audio):
  video_path_base = os.path.basename(video_path)
  basename = video_path_base.split('.')
  path_audio = basename[0]+'.'+'wav'
  print(path_audio)
  
  subprocess.call(['ffmpeg','-i' ,video_path, path_audio])
  return path_audio

