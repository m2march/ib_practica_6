#-*- coding: utf-8 -*-
import pytest
import ib
import ejercicio
import pdb
from decimal import Decimal

# Tests de los módulos

def test_is_compatible():
    "Test para la función _is_compatible de BinaryEvent."
    A = ib.BinaryEvent()
    B = ib.BinaryEvent()
    C = ib.BinaryEvent()
    X = ib.BinaryEvent({A: 1, B: 1, C: 1})

    assert X._is_compatible({A, B}, {}) == True
    assert X._is_compatible({A, B}, {A: True}) == True
    assert X._is_compatible({B}, {A: True}) == False
    assert X._is_compatible({B}, {A: True, B: True}) == False
    assert X._is_compatible({B}, {B: True}) == True
    assert X._is_compatible({B}, {B: False}) == False


# Earthquake: Evaluamos el módulo ib con el ejemplo de terremoto de la clase 4

## Definimos el modelo
beta = Decimal('0.001')
epsilon = Decimal('0.001')
f = Decimal('0.001')
alpha_b = Decimal('0.99')
alpha_e = Decimal('0.01')
one = Decimal('1')

Earthquake = ib.BinaryEvent(gamma=epsilon, name='Earthquake')
Bulglar = ib.BinaryEvent(gamma=beta, name='Bulglar')
Radio = ib.BinaryEvent({Earthquake: one}, name='Radio')
Alarm = ib.BinaryEvent({Bulglar: alpha_b, Earthquake: alpha_e}, gamma=f,
                       name='Alarm')
Phonecall = ib.BinaryEvent({Alarm: one}, name='Phonecall')

def test_earthquake_full_deps():
    "Evaluamos el cálculo de las dependencias completas."

    assert Earthquake._prob_pos() == f
    assert Earthquake._prob_neg() == one - f

    assert Bulglar.prob_pos() == pytest.approx(0.001)
    assert Bulglar.prob_neg() == pytest.approx(1 - 0.001)

    assert (Alarm._prob_neg({Bulglar: False, Earthquake: False}) == 
            (one - f))
    assert (Alarm.prob_neg({Bulglar: True, Earthquake: False}) == 
            pytest.approx(float((1 - f) * (1 - alpha_b))))
    assert (Alarm.prob_neg({Bulglar: False, Earthquake: True}) ==
            pytest.approx(float((1 - f) * (1 - alpha_e))))
    assert (Alarm.prob_neg({Bulglar: True, Earthquake: True}) ==
            pytest.approx(float((1 - f) * (1 - alpha_b) * (1 - alpha_e))))

    assert (Alarm.prob_pos({Bulglar: False, Earthquake: False}) ==
            pytest.approx(float(f)))
    assert (Alarm.prob_pos({Bulglar: True, Earthquake: False}) == 
           pytest.approx(float(1 - ((1 - f) * (1 - alpha_b)))))
    assert (Alarm.prob_pos({Bulglar: False, Earthquake: True}) == 
           pytest.approx(float(1 - ((1 - f) * (1 - alpha_e)))))
    assert (Alarm.prob_pos({Bulglar: True, Earthquake: True}) == 
           pytest.approx(float(1 - ((1 - f) * (1 - alpha_e) * (1 - alpha_b)))))

    assert (Phonecall.prob_pos({Alarm: True}) == 1)
    assert (Phonecall.prob_pos({Alarm: False}) == 0)
    
    assert (Radio.prob_pos({Earthquake: True}) == 1)
    assert (Radio.prob_pos({Earthquake: False}) == 0)


def test_earthquake_partial_deps():
    "Evaluamos el cálculo de algunas dependencias parciales."

    alarm_partial_b_true = Alarm.prob_pos({Bulglar: True})
    alarm_partial_b_false = Alarm.prob_pos({Bulglar: False})
    assert (alarm_partial_b_true == 
            pytest.approx(Alarm.prob_pos({Bulglar: True, Earthquake: True}) *
                          Earthquake.prob_pos() +
                          Alarm.prob_pos({Bulglar: True, Earthquake: False}) *
                          Earthquake.prob_neg()))
    assert (alarm_partial_b_false == 
            pytest.approx(Alarm.prob_pos({Bulglar: False, Earthquake: True}) *
                          Earthquake.prob_pos() +
                          Alarm.prob_pos({Bulglar: False, Earthquake: False}) *
                          Earthquake.prob_neg()))

    alarm_partial = Alarm.prob_pos()
    assert (alarm_partial == pytest.approx(
        alarm_partial_b_true * Bulglar.prob_pos() +
        alarm_partial_b_false * Bulglar.prob_neg()))
