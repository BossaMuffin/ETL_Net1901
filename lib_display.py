#!/usr/bin/env python
# coding: utf-8

# # Bossa Muffin Functions Display Library v1 - 24/04/2022 
# # to import in all my program
import time

# Function which displays an empty line in the consol 
def printn(p_nb=1):
    for l_i in range(p_nb):
        print('\n')


# Function which displays full line in the consol 
def printl(p_nb=10):
     print('-'*p_nb)

# Function which returns full line
def separator(p_nb=10):
     return '-'*p_nb


# Function which delays the program by x laps of y steps (defaut 1)
def countdown(p_laps, p_show=True, p_step=1, p_space=2):
    e_global_time = p_laps*p_step
    if p_show:
        printn(p_space)
        print('Waiting...', e_global_time, 's ...', end=' ')
    if p_laps!= 0: time.sleep(1)
    for l_i in range(e_global_time)[1:]:
        if p_show and l_i%p_step == 0:
            print(p_laps*p_step-l_i, '...', end=' ')
        time.sleep(1)
    if p_show:
        print('GO!')
        printn(p_space)
