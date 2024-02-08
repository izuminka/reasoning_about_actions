


(define (problem mixed-f2-p7-u0-v0-d0-a0-n0-A0-B0-N0-F0)
   (:domain miconic)
   (:objects p0 p1 p2 p3 p4 p5 p6 - passenger
             f0 f1 - floor)


(:init
(above f0 f1)



(origin p0 f1)
(destin p0 f0)

(origin p1 f0)
(destin p1 f1)

(origin p2 f1)
(destin p2 f0)

(origin p3 f0)
(destin p3 f1)

(origin p4 f0)
(destin p4 f1)

(origin p5 f0)
(destin p5 f1)

(origin p6 f0)
(destin p6 f1)






(lift-at f0)
)


(:goal


(and
(served p0)
(served p1)
(served p2)
(served p3)
(served p4)
(served p5)
(served p6)
))
)


