(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	satellite1 - satellite
	instrument1 - instrument
	instrument2 - instrument
	satellite2 - satellite
	instrument3 - instrument
	spectrograph3 - mode
	spectrograph1 - mode
	spectrograph2 - mode
	thermograph0 - mode
	thermograph4 - mode
	Star2 - direction
	Star1 - direction
	GroundStation0 - direction
	Star3 - direction
	Planet4 - direction
	Star5 - direction
	Phenomenon6 - direction
	Star7 - direction
	Star8 - direction
)
(:init
	(supports instrument0 spectrograph1)
	(calibration_target instrument0 Star1)
	(on_board instrument0 satellite0)
	(power_avail satellite0)
	(pointing satellite0 Star1)
	(supports instrument1 thermograph4)
	(supports instrument1 spectrograph2)
	(supports instrument1 spectrograph3)
	(calibration_target instrument1 Star1)
	(supports instrument2 thermograph4)
	(supports instrument2 spectrograph1)
	(supports instrument2 thermograph0)
	(calibration_target instrument2 GroundStation0)
	(on_board instrument1 satellite1)
	(on_board instrument2 satellite1)
	(power_avail satellite1)
	(pointing satellite1 Star8)
	(supports instrument3 spectrograph2)
	(calibration_target instrument3 GroundStation0)
	(on_board instrument3 satellite2)
	(power_avail satellite2)
	(pointing satellite2 Star7)
)
(:goal (and
	(pointing satellite1 Star1)
	(pointing satellite2 Star2)
	(have_image Star3 spectrograph3)
	(have_image Planet4 thermograph0)
	(have_image Star5 spectrograph1)
	(have_image Phenomenon6 spectrograph3)
	(have_image Star7 spectrograph1)
	(have_image Star8 spectrograph1)
))

)
