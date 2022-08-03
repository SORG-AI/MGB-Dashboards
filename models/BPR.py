import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
from torch.utils import data
from glob import glob
import os
#from google.colab import drive
import time 
#drive.mount('/content/drive')
import torchvision.models as models

from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

import matplotlib.pyplot as plt

from torch.utils.data import DataLoader

import csv
if torch.cuda.is_available():
    device = torch.device('cuda')
else:
    device = torch.device('cpu')


transform = transforms.Compose([transforms.Resize((224,224)), transforms.ToTensor()])
classes = ('Ankle', 'Elbow', 'Foot', 'Hand', 'Hip', 'Knee', 'Shoulder', 'Spine',  'Wrist')
def check_image(path):  
    try:
        im = Image.open(path)
        return True
    except:
        return False
        
import os        
model_dir= os.path.join('..','models')
path_dir = os.path.join('..','data','bpr_image')
print(path_dir)
#path_to_image = r'C:\Users\bardi\dev\fixus-app\data\default_images\Fracture_No_01.png'


test_data = torchvision.datasets.ImageFolder(root=path_dir,transform=transform)
test_data_loader = torch.utils.data.DataLoader(test_data, batch_size=1, shuffle=False, num_workers=2)

num_classes = 9
model=models.resnet50(pretrained=True)
model.fc = nn.Sequential(nn.Linear(model.fc.in_features,512), nn.ReLU(), nn.Dropout(), nn.Linear(512, num_classes))
model.load_state_dict(torch.load(os.path.join(model_dir,'BPR9.pt')))
model.eval()
#model.to('cuda')

def test_model(model):
    list_o=[]
    list_x=[]
    list_prob=[]
    correct = 0
    total = 0
    with torch.no_grad():        
        for i, (images, labels) in enumerate(test_data_loader):
            
#            imshow(torchvision.utils.make_grid(images))
            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            #print(predicted)
            probs=outputs.data.cpu().numpy().reshape(-1)
            fname, _ = test_data_loader.dataset.samples[i]
            contents=[labels, predicted.item(), fname, probs]
            out=F.softmax(outputs, dim=-1)
            if not predicted == labels:
                print(fname)
                print(predicted)
                print(outputs.data.cpu().numpy().reshape(-1))
                list_x.append(contents)
            else:
                list_o.append(contents)
            list_prob.append([fname, out])
    print('correct: {:d}  total: {:d}'.format(correct, total))
    print('accuracy = {:f}'.format(correct / total))
    with open(model_dir+'/file_correct16_1000.csv', 'w', newline='')as file:
        writer=csv.writer(file, quoting=csv.QUOTE_ALL, delimiter=';')
        writer.writerows(list_o)
    with open(model_dir+'/file_wrong16_1000.csv', 'w', newline='')as file:
        writer=csv.writer(file, quoting=csv.QUOTE_ALL, delimiter=';')
        writer.writerows(list_x)
    with open(model_dir+'/file_softprob16_1000.csv', 'w', newline='')as file:
        writer=csv.writer(file, quoting=csv.QUOTE_ALL, delimiter=';')
        writer.writerows(list_prob)

start_time = time.time()
test_model(model)
print(time.time()-start_time)
