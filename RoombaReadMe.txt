Hello! This is a brief summary of the attached image folders.

I've posted three different folders. Two contains pictures of roombas, and one containing pictures of floors without roombas. The two folders that contain roombas are supposed to be a single folder full of roombas, but github caps files at 25mb so I had to split up my roomba images into two folders before I uploaded them. That being said before you use the folders I uploaded please put all of the images from roomba & roomba1 into a single folder.

The reasoning behind this choice of image sets is that all pictures of roombas have a floor as a background, so I figured a image set of just floors would be a decent control to use when attemping to train a nueral network to detect roombas. 

But these image sets sadly fail to produce good results. The accuracy of the image classifier I used (which is simply a retrained version of a TensorFlow classifier) has an accuracy that is unrealistically high. This means that the image sets are likely flawed.

I am guessing that the image sets too different and that the classifier is latching onto these major (unintended) differences. One other problem may be that there are too many frames taken from the competition advertisement video that directly follow one another in the origanal video. In other words, many of the images in the data sets may look like copies of each other to the classifier, as the differences between these images are quite small.

To wrap things up, nueral networks are really good at latching on to unintended discrepencies in data sets, and I am guessing that is what has happened in this case. In the future it may be best to first start out by creating a data set from scratch using pictures you have taken, and seeing how that works before moving onto a more general classifier to ensure that the mistake isn't inherent to the way the data sets are set up. Other than that you can start by editing the data sets I've posted along with this readme to see if you can get better results then I did.

Sorry for any typos or formating errors. I typed this up super fast in a text editor without a spellchecker, so I hope its at least somewhat understandable. 

But, if you find it isn't, or if you want me to clarify anything feel free to contact me at pickense@carleton.edu.
