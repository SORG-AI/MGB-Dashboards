## Load Libraries
import os
import numpy as np

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import tensorflow as tf
from tensorflow.keras import layers, models

# import sys
# if r"C:\Users\bardi\Dropbox (Partners HealthCare)\DL Projects\DL_Codes" not in sys.path:
#     sys.path.append(r"C:\Users\bardi\Dropbox (Partners HealthCare)\DL Projects\DL_Codes")
# if r"C:\Users\bardi\Dropbox (Partners HealthCare)\DL Projects\DL_ImagingCodes" not in sys.path:
#     sys.path.append(r"C:\Users\bardi\Dropbox (Partners HealthCare)\DL Projects\DL_ImagingCodes")

import argparse

## Preprocess the Image
import imutil_manipulate as im_man

## Show the results
import matplotlib.pyplot as plt

def load_user_inputs():
    # Model Loading
    path_to_model = os.path.join('..', 'models', r'model_hip_fracture.h5')
    #model       = models.load_model(path_to_model)


    return path_to_model


def classify_fracture(path_images):
    ## Load the Model
    # Model Hyperparameters
    image_width = 1062 #384
    image_height = 1062 #384
    max_im_size = image_width
    n_channel = 3
    class_names = ['Control','Fracture']




    ### 1) LOAD USER INPUTS
    path_to_model = load_user_inputs()


    ## 2) Load the model
    model       = models.load_model(path_to_model)


    

    # [CHECK] 3) Check the number of images user have uploaded
    n_unlabeled = len(path_images)
    if n_unlabeled>10:
        raise ValueError('You cannot upload more than 10 images')



    # 3) Making the predictions
    student_images = np.zeros((n_unlabeled, image_width, image_height, n_channel))


    # Loop through each image and classify
    student_path = []


    ## Preprocessing
    for image_id, path_image in enumerate(path_images):
        im_data = im_man.im_preprocess(path_image, (max_im_size, max_im_size), 0, debugging=False)


        for channel in range(n_channel):
            student_images[image_id, :, :, channel] = im_data


    # Use the Model to Predict the Image
    student_images = student_images.astype(np.uint8)


    prediction_prob = model.predict(student_images)    
    prediction = tf.argmax(input=prediction_prob, axis=1).numpy()




    for student_id, student_image in enumerate(student_images):

        predicted_class = prediction[student_id]
        
        
        fig, axs = plt.subplots(ncols=2, nrows=1, dpi=100)
        
        #if not predicted_class:
            

        
        if not predicted_class:
            gs = axs[1].get_gridspec()
            # remove the underlying axes
            for ax in axs:
                ax.remove()
            axbig = fig.add_subplot(gs[0:])
                        
            axbig.imshow(student_image, cmap='gray') #test_images
            #plt.xlabel('{}'.format(incorrect_names[i]))  
            axbig.set_title('{} ({:.2f}% Confidence)'.format(class_names[predicted_class],
                                                 prediction_prob.max(axis=1)[student_id]*100))    
            #print(prediction_prob)
            #ax.set_title()
            axbig.axis('off')

        
        else:
            axs[0].imshow(student_image, cmap='gray') #test_images
            #plt.xlabel('{}'.format(incorrect_names[i]))  
            
            #axs[0].set_title('{}\n{} ({:.2f}% Confidence)'.format(path_image.split('\\')[-1],
            #                                     class_names[predicted_class],
            #                                     prediction_prob.max(axis=1)[student_id]*100))    
            
            axs[0].set_title('{} ({:.2f}% Confidence)'.format(class_names[predicted_class],
                                                 prediction_prob.max(axis=1)[student_id]*100))                                                   
            #print(prediction_prob)
            #ax.set_title()
            axs[0].axis('off')
        
            import DL_EvalHelpers as util
            normalized_tensor = util.return_saliency(model, student_image, predicted_class)
            normalized_tensor = normalized_tensor.numpy()
            normalized_tensor = np.ma.masked_where(normalized_tensor < 5, normalized_tensor) # Why 4?
            
            axs[1].imshow(student_image, cmap='gray')
            axs[1].imshow(normalized_tensor, cmap='hot', alpha = 0.5)
            axs[1].set_title('Detected Region of Fracture')        
            axs[1].axis('off')
        
        
        plt.show()    




if __name__ == "__main__":
    
    path_default_data = os.path.join('..','data','default_hip')
    images_default_list = [os.path.join(path_default_data, 'Fracture_No_01.png'),
                           os.path.join(path_default_data, 'Fracture_Yes_01.png')]
    
    parser = argparse.ArgumentParser(description="Load Images")
    parser.add_argument('--path-images', '-f', nargs="*", default=images_default_list, help="filepath to the image")
    args = parser.parse_args()
    
    #print(vars(args))
    #print(args.path_images)

    path_images = [os.path.normpath(this_path.strip(',')) for this_path in args.path_images]
    
    
    classify_fracture(path_images)
    #path_images = "C:\Users\bardi\Dropbox (Partners HealthCare)\DL Projects\Tutorials\Images\Data\Hip_Dataset\Y\15343701_DX_AP_017013_000001.png", "C:\Users\bardi\Dropbox (Partners HealthCare)\DL Projects\Tutorials\Images\Data\Hip_Dataset\N\13624793_DX_AP_036187_000004.png"
