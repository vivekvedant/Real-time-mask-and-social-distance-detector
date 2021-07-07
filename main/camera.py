import cv2
from  main.object_predictors import Predictors

class LiveWebCam:
	def __init__(self,rtsp_link):
		self.url = cv2.VideoCapture(rtsp_link)

	def __del__(self):
		cv2.destroyAllWindows()

	def get_mask_frame(self,user_name):
		detectors= Predictors()
		success,imgNp = self.url.read()
		frame = detectors.get_mask_detector(imgNp,user_name)
		ret, jpeg = cv2.imencode('.jpg', frame)
		
		return jpeg.tobytes() 

	
	def get_pedistran_frame(self,user_name):
		detectors= Predictors()
		success,imgNp = self.url.read()
		frame = detectors.get_pedistran_detector(imgNp,user_name)
		ret, jpeg = cv2.imencode('.jpg', frame)
		return jpeg.tobytes() 