(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	instrument1 - instrument
	satellite1 - satellite
	instrument2 - instrument
	instrument3 - instrument
	spectrograph2 - mode
	spectrograph1 - mode
	spectrograph0 - mode
	infrared3 - mode
	thermograph4 - mode
	Star1 - direction
	GroundStation3 - direction
	GroundStation5 - direction
	Star0 - direction
	Star8 - direction
	GroundStation2 - direction
	GroundStation4 - direction
	GroundStation9 - direction
	Star7 - direction
	Star6 - direction
	Star10 - direction
	Star11 - direction
	Star12 - direction
	Star13 - direction
	Planet14 - direction
	Phenomenon15 - direction
	Star16 - direction
)
(:init
	(supports instrument0 spectrograph0)
	(supports instrument0 thermograph4)
	(calibration_target instrument0 GroundStation2)
	(calibration_target instrument0 GroundStation4)
	(calibration_target instrument0 Star0)
	(supports instrument1 spectrograph1)
	(supports instrument1 spectrograph0)
	(calibration_target instrument1 GroundStation2)
	(calibration_target instrument1 GroundStation4)
	(calibration_target instrument1 Star8)
	(on_board instrument0 satellite0)
	(on_board instrument1 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Star1)
	(supports instrument2 spectrograph0)
	(supports instrument2 spectrograph2)
	(supports instrument2 infrared3)
	(calibration_target instrument2 Star7)
	(calibration_target instrument2 GroundStation9)
	(calibration_target instrument2 GroundStation4)
	(supports instrument3 spectrograph2)
	(supports instrument3 spectrograph1)
	(calibration_target instrument3 Star6)
	(on_board instrument2 satellite1)
	(on_board instrument3 satellite1)
	(power_avail satellite1)
	(pointing satellite1 GroundStation4)
)
(:goal (and
	(pointing satellite1 Star0)
	(have_image Star10 spectrograph1)
	(have_image Star11 thermograph4)
	(have_image Star12 spectrograph1)
	(have_image Star13 spectrograph0)
	(have_image Planet14 spectrograph1)
	(have_image Phenomenon15 spectrograph0)
	(have_image Star16 spectrograph0)
))

)
