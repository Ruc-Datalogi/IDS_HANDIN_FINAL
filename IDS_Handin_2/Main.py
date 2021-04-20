import cv2
import mediapipe as mp
import random
from StaticVariables import *
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

## Game on ## 
game_on = False

## Font for displaying strings ##
font = cv2.FONT_HERSHEY_SIMPLEX


# For webcam input:
cap = cv2.VideoCapture(0)
success, image = cap.read()
image_height, image_width, _ = image.shape
image_counter = 0


## The player ##
x_pos_player = int(image_width - 22)
y_pos_player = int(image_height/2)
y_vel_player = 0


## The computer ##
x_pos_computer = 10 
y_pos_computer = 10

x_vel_computer = 0
y_vel_computer = 10

computer_direction = 0

## Start ball pos ##
ball_pos = [100, 150]

ball_vel = [6,6]
score = [0,0] 

## Color for the rectangles ##
color = (0,0,255)

## Get the player vel ##
def get_player_vel(hand_y_pos, player_y_pos):
    
    ## No movement if the hand is close to the rectangle ##
    if abs(player_y_pos - hand_y_pos)/(player_y_pos+hand_y_pos/2) < 0.02:
      return 0


    ## Move up if the hand is over the rect and move down if the opposite is true ##
    if hand_y_pos > player_y_pos and y_pos_player < 400:
        return 8
    elif hand_y_pos < player_y_pos  and y_pos_player > 0:
        return -8

    ## We have to return a number ##
    else:
        return 0


## Function for moving the player ##
def move_player(y_pos_player, y_vel_player):
    y_pos_player += y_vel_player


    ## Making sure the rectangle does not go out of bounds ##
    if y_pos_player > StaticVariables.IMAGE_HEIGHT - StaticVariables.PLAYER_SIZE[1]:
        y_pos_player = 400
    
    if y_pos_player < 0:
        y_pos_player = 0
    
    return y_pos_player


def move_computer(com_pos, com_vel, ball_pos, computer_direction):
    computer_direction += 1

    ## Let's wait 2 frame before changing direction
    if ball_pos[1] - com_pos < StaticVariables.BALL_SIZE and 2 < computer_direction :
        com_vel = -10
        computer_direction = 0
        
    elif 2 < computer_direction:
        com_vel = 10
        computer_direction = 0

    com_pos += com_vel

    ## Make sure we stay within the boundrary##    
    if com_pos > StaticVariables.IMAGE_HEIGHT - StaticVariables.PLAYER_SIZE[1]:
        com_pos = 400
    if com_pos < 0:
        com_pos = 0

    return com_pos, com_vel, computer_direction


def check_score(ball_pos, score):
    if ball_pos[0] < 0:
        score[1] += 1
        ball_pos = respawn_ball(ball_pos)
    elif ball_pos[1] > image_width - 14:
        score[0] += 1
        ball_pos = respawn_ball(ball_pos)


def move_ball(ball_pos,ball_vel, image_height, image_width):
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    #if ball_pos[0] > image_width - 14:
    #    ball_vel[0] *= -1

    #if ball_pos[0] < 0:
    #    ball_vel[0] *= -1
    
    if ball_pos[1] > StaticVariables.IMAGE_HEIGHT - StaticVariables.BALL_SIZE:
        ball_pos[1] = StaticVariables.IMAGE_HEIGHT - StaticVariables.BALL_SIZE
        ball_vel[1] *= -1
    
    if ball_pos[1] < 0:
        ball_pos[1] = 0
        ball_vel[1] *= -1


    return ball_pos, ball_vel

def ball_collision(ball_pos, ball_vel, y_pos_computer, y_pos_player, score):

    if 10 < ball_pos[0] < 22 :
        if ball_pos[1] > y_pos_computer and ball_pos[1] < (y_pos_computer + 80):
           ball_pos[0] = 23
           ball_vel[0] *= -1
        

    ## To make sure we are behind the rect and then update the score##
    if ball_pos[0] < 0 + StaticVariables.BALL_SIZE:
        ball_pos[0] = 250
        ball_pos[1] = 250
        ball_vel[0] *= -1
        score[1] += 1

    ## - 14 because of the balls size ## 
    elif 618 - 14 < ball_pos[0] < 630 + 14:
        
        if ball_pos[1] > y_pos_player and ball_pos[1] < (y_pos_player + 80):
            ball_pos[0] = (640 - 44)
            ball_vel[0] *= -1

    
    ## To make sure we are behind the player and then update the score##    
    if 640 - StaticVariables.BALL_SIZE < ball_pos[0]:
        ball_pos[0] = 250
        ball_pos[1] = 250
        ball_vel[0] *= -1
        score[0] += 1
    
    return ball_vel, ball_pos


with mp_hands.Hands(

    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        y_vel_player = get_player_vel(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height, y_pos_player)

        if(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height < 50):
            game_on = True
        mp_drawing.draw_landmarks(
            image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    ## Play Game ##
    if game_on:
        y_pos_computer, y_vel_computer, computer_direction = move_computer(y_pos_computer, y_vel_computer, ball_pos, computer_direction)
        y_pos_player = move_player(y_pos_player,y_vel_player)

        ball_vel, ball_pos = ball_collision(ball_pos,ball_vel,y_pos_computer,y_pos_player, score)
        ball_pos, ball_vel = move_ball(ball_pos, ball_vel, image_height, image_width)
        #check_score(ball_pos, score)
        
        ## Drawing Computer ##
        image = cv2.rectangle(image,(x_pos_computer,y_pos_computer),(x_pos_computer + StaticVariables.PLAYER_SIZE[0] ,y_pos_computer + StaticVariables.PLAYER_SIZE[1]),color,-1)

        ## Drawing Player ##
        image = cv2.rectangle(image,(x_pos_player,y_pos_player),(x_pos_player + StaticVariables.PLAYER_SIZE[0] , y_pos_player + StaticVariables.PLAYER_SIZE[1]),color,-1)

        ## Drawing Ball ##
        image = cv2.rectangle(image,(ball_pos[0],ball_pos[1]),(ball_pos[0] + StaticVariables.BALL_SIZE ,ball_pos[1] + StaticVariables.BALL_SIZE), color, -1)

        ## Score for the player and computer ##
        cv2.putText(image,str(score[0]),(int((image_width / 2)-60),40),font,1,(0,0,0))
        cv2.putText(image,str(score[1]),(int((image_width / 2)+60),40),font,1,(0,0,0))

    ## Show start screen ##
    else:
        cv2.putText(image,'You control with the tip', (0 , 60),font,1,(0,0,0))
        cv2.putText(image,'of your index finger!', (0 , 100),font,1,(0,0,0))
        cv2.putText(image,'Raise your finger to start the game', (0 , 140),font , 1 ,(0,0,0))
        cv2.putText(image,'Press space to take a picture :)', (0, 240), font , 1 ,(0,0,0))

    cv2.imshow('PING PONG', image)

    ## To escape the program ## 
    key = cv2.waitKey(5)

    ## Escape pressed ##
    if key % 256 == 27:
        break

    ## Press space to take a picture ##
    elif key % 256 == 32:
        image_name = "Ping_Pong_ScreenShot{}.png".format(random.randint(0,10000000))
        cv2.imwrite("IDS_Handin_2/Saved_Images/"+ str(image_name), image)
        


cap.release()