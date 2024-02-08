(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	infrared2 - mode
	infrared4 - mode
	spectrograph3 - mode
	spectrograph1 - mode
	infrared5 - mode
	infrared0 - mode
	GroundStation0 - direction
	GroundStation1 - direction
	Planet2 - direction
)
(:init
	(supports instrument0 spectrograph3)
	(supports instrument0 infrared4)
	(supports instrument0 infrared5)
	(supports instrument0 infrared0)
	(supports instrument0 spectrograph1)
	(supports instrument0 infrared2)
	(calibration_target instrument0 GroundStation1)
	(on_board instrument0 satellite0)
	(power_avail satellite0)
	(pointing satellite0 GroundStation1)
)
(:goal (and
	(have_image Planet2 spectrograph3)
	(have_image Planet2 spectrograph1)
))

)
