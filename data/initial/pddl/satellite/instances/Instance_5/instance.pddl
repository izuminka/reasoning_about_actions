(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	satellite1 - satellite
	instrument1 - instrument
	instrument2 - instrument
	thermograph0 - mode
	thermograph2 - mode
	infrared4 - mode
	spectrograph5 - mode
	infrared1 - mode
	thermograph3 - mode
	GroundStation1 - direction
	GroundStation2 - direction
	GroundStation3 - direction
	GroundStation0 - direction
	Star4 - direction
	Phenomenon5 - direction
	Phenomenon6 - direction
	Phenomenon7 - direction
)
(:init
	(supports instrument0 infrared4)
	(supports instrument0 thermograph2)
	(calibration_target instrument0 GroundStation0)
	(on_board instrument0 satellite0)
	(power_avail satellite0)
	(pointing satellite0 GroundStation0)
	(supports instrument1 thermograph3)
	(supports instrument1 spectrograph5)
	(calibration_target instrument1 GroundStation0)
	(supports instrument2 infrared1)
	(supports instrument2 thermograph0)
	(supports instrument2 infrared4)
	(calibration_target instrument2 GroundStation0)
	(on_board instrument1 satellite1)
	(on_board instrument2 satellite1)
	(power_avail satellite1)
	(pointing satellite1 Star4)
)
(:goal (and
	(pointing satellite0 Star4)
	(have_image Star4 spectrograph5)
	(have_image Star4 infrared1)
	(have_image Phenomenon5 spectrograph5)
	(have_image Phenomenon6 thermograph3)
	(have_image Phenomenon6 thermograph2)
	(have_image Phenomenon7 infrared1)
))

)
