(define (problem strips-sat-x-1)
(:domain satellite)
(:objects
	satellite0 - satellite
	instrument0 - instrument
	satellite1 - satellite
	instrument1 - instrument
	instrument2 - instrument
	instrument3 - instrument
	satellite2 - satellite
	instrument4 - instrument
	instrument5 - instrument
	instrument6 - instrument
	satellite3 - satellite
	instrument7 - instrument
	instrument8 - instrument
	satellite4 - satellite
	instrument9 - instrument
	instrument10 - instrument
	instrument11 - instrument
	thermograph3 - mode
	thermograph1 - mode
	infrared0 - mode
	infrared2 - mode
	infrared4 - mode
	GroundStation0 - direction
	Star3 - direction
	GroundStation2 - direction
	Star1 - direction
	Star4 - direction
	Star5 - direction
)
(:init
	(supports instrument0 thermograph3)
	(supports instrument0 infrared0)
	(supports instrument0 infrared4)
	(calibration_target instrument0 GroundStation2)
	(on_board instrument0 satellite0)
	(power_avail satellite0)
	(pointing satellite0 GroundStation0)
	(supports instrument1 infrared4)
	(supports instrument1 thermograph1)
	(calibration_target instrument1 Star3)
	(supports instrument2 infrared4)
	(supports instrument2 infrared0)
	(calibration_target instrument2 GroundStation0)
	(supports instrument3 thermograph1)
	(supports instrument3 thermograph3)
	(supports instrument3 infrared4)
	(calibration_target instrument3 Star4)
	(on_board instrument1 satellite1)
	(on_board instrument2 satellite1)
	(on_board instrument3 satellite1)
	(power_avail satellite1)
	(pointing satellite1 Star3)
	(supports instrument4 infrared4)
	(supports instrument4 thermograph3)
	(calibration_target instrument4 Star3)
	(supports instrument5 thermograph3)
	(calibration_target instrument5 Star4)
	(supports instrument6 infrared4)
	(supports instrument6 infrared0)
	(supports instrument6 thermograph3)
	(calibration_target instrument6 Star3)
	(on_board instrument4 satellite2)
	(on_board instrument5 satellite2)
	(on_board instrument6 satellite2)
	(power_avail satellite2)
	(pointing satellite2 Star1)
	(supports instrument7 infrared4)
	(supports instrument7 thermograph3)
	(calibration_target instrument7 GroundStation2)
	(supports instrument8 thermograph3)
	(supports instrument8 infrared4)
	(supports instrument8 thermograph1)
	(calibration_target instrument8 Star1)
	(on_board instrument7 satellite3)
	(on_board instrument8 satellite3)
	(power_avail satellite3)
	(pointing satellite3 Star1)
	(supports instrument9 thermograph3)
	(calibration_target instrument9 Star1)
	(supports instrument10 infrared0)
	(supports instrument10 infrared4)
	(supports instrument10 infrared2)
	(calibration_target instrument10 Star1)
	(supports instrument11 infrared2)
	(calibration_target instrument11 Star4)
	(on_board instrument9 satellite4)
	(on_board instrument10 satellite4)
	(on_board instrument11 satellite4)
	(power_avail satellite4)
	(pointing satellite4 Star3)
)
(:goal (and
	(pointing satellite3 Star4)
	(pointing satellite4 GroundStation2)
	(have_image Star5 infrared4)
))

)
