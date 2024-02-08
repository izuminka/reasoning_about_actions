(define (problem grid-7)
(:domain grid-visit-all)
(:objects 
	loc-x3-y0
	loc-x4-y0
- place 
        
)
(:init
	(at-robot loc-x4-y0)
	(visited loc-x4-y0)
	(connected loc-x3-y0 loc-x4-y0)
 	(connected loc-x4-y0 loc-x3-y0)
 
)
(:goal
(and 
	(visited loc-x3-y0)
	(visited loc-x4-y0)
)
)
)
