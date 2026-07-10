import pygame

import math
import random

#initialize pygame window
pygame.init()
screenWidth = 800
screenHeight = 600
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Fast Conway's Game of Life - Graphs")

#fps display
clock = pygame.time.Clock()
def displayFPS(screen, font_size):
    font = pygame.font.SysFont(None, font_size)
    fps = round(clock.get_fps(), 1)
    fps_text = font.render(f"{fps}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

#CLASS DEFINITION -----------------------------------------------------------------------------------------------------------------------------------------

#FUNCTION DEFINITION - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def drawGraph(values, color, connectDots, left, bottom, width, height, highestvalue):
    points = []

    for i in range(len(values)):
        xOffset = ((i+1)/len(values)) * width
        yOffset = (values[i] / highestvalue) * height

        if connectDots == False:
            pygame.draw.circle(screen, color, (left + xOffset, bottom - yOffset), 2)
        else:
            points.append((left + xOffset, bottom - yOffset))

    #draw lines between points if connectDots
    if connectDots:
        for i in range(1, len(points)):
            pygame.draw.line(screen, color, points[i-1], points[i], 2)


#VARIABLE INITIALIZATION -----------------------------------------------------------------------------------------------------------------------------------------

#get initial ticks
prevT = pygame.time.get_ticks()

# RANDOM 400 writes ----------------------------------------------------------------------------------------------

#read data
def getAccumulated(filePath):
    raw = []
    with open(filePath, "r") as f:
        raw = [float(line.strip()) for line in f]

    accumulated = []
    for i in range(len(raw)):
        value = 0
        for j in range(i):
            value += raw[j]
        accumulated.append(value)

    return accumulated

acc_pp_cgol = getAccumulated(r"Source/DataProccessing/Data/data_pp_cgol.txt")
acc_pp_icgol = getAccumulated(r"Source/DataProccessing/Data/data_pp_icgol.txt")
acc_pp_licgol = getAccumulated(r"Source/DataProccessing/Data/data_pp_licgol.txt")

acc_cr_cgol = getAccumulated(r"Source/DataProccessing/Data/data_cr_cgol.txt")
acc_cr_licgol = getAccumulated(r"Source/DataProccessing/Data/data_cr_licgol.txt")
acc_cr_licgol_flagged = getAccumulated(r"Source/DataProccessing/Data/data_cr_licgol_flagged.txt")
acc_cr_licgol_atomic = getAccumulated(r"Source/DataProccessing/Data/data_cr_licgol_atomic.txt")
acc_cr_licgol_multithreaded = getAccumulated(r"Source/DataProccessing/Data/data_cr_licgol_multithreaded.txt")

all = acc_pp_cgol + acc_pp_icgol + acc_pp_licgol + acc_cr_cgol + acc_cr_licgol + acc_cr_licgol_flagged + acc_cr_licgol_atomic + acc_cr_licgol_multithreaded
#all = acc_pp_icgol + acc_pp_licgol + acc_cr_cgol + acc_cr_licgol + acc_cr_licgol_flagged + acc_cr_licgol_atomic + acc_cr_licgol_multithreaded
#all = acc_cr_cgol + acc_cr_licgol + acc_cr_licgol_flagged + acc_cr_licgol_atomic + acc_cr_licgol_multithreaded
#all = acc_cr_licgol + acc_cr_licgol_flagged + acc_cr_licgol_atomic + acc_cr_licgol_multithreaded
highest = max(all)

#set text
font = pygame.font.Font(None, 20)

txt_pp_cgol = font.render("pp_cgol", True, (0, 255, 0))
txt_pp_icgol = font.render("pp_icgol", True, (200, 0, 0))
txt_pp_licgol = font.render("pp_licgol", True, (255, 0, 0))

txt_cr_cgol = font.render("cr_cgol", True, (0, 0, 150))
txt_cr_licgol = font.render("cr_licgol", True, (0, 0, 200))
txt_cr_licgol_flagged = font.render("cr_licgol_flagged", True, (0, 0, 255))

txt_cr_licgol_atomic = font.render("cr_licgol_atomic", True, (200, 200, 0))
txt_cr_licgol_multithreaded = font.render("cr_licgol_multithreaded", True, (255, 255, 0))

#WHILE LOOP - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

hasSavedImage = False

running = True
while running:

    #update delta time
    currT = pygame.time.get_ticks()
    dTms = currT - prevT
    dTs = dTms / 1000.0

    #fill screen
    screen.fill((0, 0, 0))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.draw.line(screen, (100, 100, 100), (50, 50), (50, 550), 1)
    pygame.draw.line(screen, (100, 100, 100), (50, 550), (750, 550), 1)

    connectDots = True
    
    drawGraph(acc_pp_cgol, (0, 255, 0), connectDots, 50, 550, 700, 500, highest)
    drawGraph(acc_pp_icgol, (200, 0, 0), connectDots, 50, 550, 700, 500, highest)
    drawGraph(acc_pp_licgol, (255, 0, 0), connectDots, 50, 550, 700, 500, highest)

    drawGraph(acc_cr_cgol, (0, 0, 150), connectDots, 50, 550, 700, 500, highest)
    drawGraph(acc_cr_licgol, (0, 0, 200), connectDots, 50, 550, 700, 500, highest)
    drawGraph(acc_cr_licgol_flagged, (0, 0, 255), connectDots, 50, 550, 700, 500, highest)
    
    drawGraph(acc_cr_licgol_atomic, (200, 200, 0), connectDots, 50, 550, 700, 500, highest)
    drawGraph(acc_cr_licgol_multithreaded, (255, 255, 0), connectDots, 50, 550, 700, 500, highest)

    #draw text
    screen.blit(txt_pp_cgol, (60, 60))

    screen.blit(txt_pp_icgol, (60, 90))
    screen.blit(txt_pp_licgol, (60, 110))

    screen.blit(txt_cr_cgol, (60, 140))
    screen.blit(txt_cr_licgol, (60, 160))
    screen.blit(txt_cr_licgol_flagged, (60, 180))

    screen.blit(txt_cr_licgol_atomic, (60, 210))
    screen.blit(txt_cr_licgol_multithreaded, (60, 230))

    # Update the display (buffer flip)
    #displayFPS(screen, 25)
    pygame.display.flip()
    clock.tick(60)

    if not hasSavedImage:
        pygame.image.save(screen, "Graph.png")

    #update delta time
    prevT = currT

# Quit Pygame
pygame.quit()
