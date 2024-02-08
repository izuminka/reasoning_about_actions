(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	spectrograph1 - mode
	infrared3 - mode
	image2 - mode
	thermograph0 - mode
	infrared4 - mode
	Star1 - direction
	Star2 - direction
	Star3 - direction
	GroundStation4 - direction
	Star5 - direction
	GroundStation7 - direction
	Star8 - direction
	GroundStation6 - direction
	GroundStation0 - direction
	Star9 - direction
	Phenomenon10 - direction
	Planet11 - direction
	Planet12 - direction
	Star13 - direction
	Phenomenon14 - direction
)
(:init
	(supports instrument0 image2)
	(supports instrument0 spectrograph1)
	(supports instrument0 infrared4)
	(supports instrument0 thermograph0)
	(supports instrument0 infrared3)
	(calibration_target instrument0 GroundStation0)
	(calibration_target instrument0 GroundStation6)
	(calibration_target instrument0 Star8)
	(on_board instrument0 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Star8)
)
(:goal (and
	(have_image Star9 thermograph0)
	(have_image Phenomenon10 thermograph0)
	(have_image Planet11 spectrograph1)
	(have_image Planet12 infrared4)
	(have_image Star13 thermograph0)
	(have_image Phenomenon14 thermograph0)
))

)
