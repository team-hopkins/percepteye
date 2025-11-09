# Percepteye

We are building this to help disabled people to navigate like face recognition, sign language gesture identification and Object detection in case of no faces or gestures.

Apart from that we have a semantic router which determines which route to trigger. So we have a RaspberryPi which has a WebCam inbuilt, and that has a client that will call the semantic router, based on the image and the audio frame the Router will route the required API.

Now we have deployed the three APIs in three VMs provisioned in Digital Ocean.
We also have created a Space in Digital Ocean, which contains the dataset for hand gesture aplhabets and that was trained in Gesture AI playground. So we used a transfer learning strategy where we have a ResNet Model trained on ImageNet and then it was fine tuned using the Dataset in the Space Storage of Digital Ocean. After training we dockerized and deployed the model to access the endpoint, that consumes an image frame as a payload and returns the output of the gesture.

We have thoughtfully leverage a hybrid model where we are using both pre-trained model as well running our own model based on the use cases.

All the three APIS are in three different Repos:

- Sign Language Detector - https://github.com/team-hopkins/sign_language_detection
- Face Recognition and TTS using 11 labs - https://github.com/team-hopkins/face_recognition
- Object Detection - https://github.com/team-hopkins/percepteye
- Semantic Router - https://github.com/team-hopkins/percepteye

We have also leveraged 11 labs for the Text to Speech for the face recognition, that helps the blind people to identify the known and unknown people.

The semantic router supports three types of routes:

- **Face Recognition + TTS API**: Identifies faces and provides audio descriptions
- **Sign Language Detection API**: Recognizes hand gestures and interprets sign language
- **Scene Description**: When no faces or hand gestures are detected, uses Gemini 2.5 Flash to describe nearby objects, helping blind users understand their surroundings
