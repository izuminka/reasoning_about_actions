(move f1-0f f2-0f)
(pickup-laser f2-0f)
(move f2-0f f1-0f)
(fire-laser f1-0f f1-1f)
(move f1-0f f1-1f)
(fire-laser f1-1f f1-2f)
(move f1-1f f1-2f)
(fire-laser f1-2f f1-3f)
(move f1-2f f1-1f)
(move f1-1f f1-0f)
(move f1-0f f2-0f)
(putdown-laser f2-0f)
(pickup-bomb f2-0f)
(move f2-0f f1-0f)
(move f1-0f f1-1f)
(move f1-1f f1-2f)
(move f1-2f f1-3f)
(detonate-bomb f1-3f f1-4f)
(move f1-3f f1-4f)
(pick-gold f1-4f)
; cost = 20 (unit cost)