(move f0-0f f1-0f)
(move f1-0f f2-0f)
(move f2-0f f3-0f)
(move f3-0f f4-0f)
(pickup-laser f4-0f)
(move f4-0f f3-0f)
(move f3-0f f2-0f)
(move f2-0f f1-0f)
(fire-laser f1-0f f1-1f)
(move f1-0f f1-1f)
(fire-laser f1-1f f1-2f)
(move f1-1f f1-0f)
(move f1-0f f2-0f)
(move f2-0f f3-0f)
(move f3-0f f4-0f)
(putdown-laser f4-0f)
(pickup-bomb f4-0f)
(move f4-0f f3-0f)
(move f3-0f f2-0f)
(move f2-0f f1-0f)
(move f1-0f f1-1f)
(move f1-1f f1-2f)
(detonate-bomb f1-2f f1-3f)
(move f1-2f f1-3f)
(pick-gold f1-3f)
; cost = 25 (unit cost)