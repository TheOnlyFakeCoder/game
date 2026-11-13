use bevy::prelude::*;
const X_EXTENT: f32 = 1000.;
const Y_EXTENT: f32 = 150.;
const THICKNESS: f32 = 5.0;

pub fn create_scenario(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<ColorMaterial>>,
) {
    commands.spawn(Camera2d);

    let shapes = [meshes.add(Rectangle::new(50.0, 10.0))];
    let num_shapes = shapes.len();

    for (i, shape) in shapes.into_iter().enumerate() {
        // Distribute colors evenly across the rainbow.
        let color = Color::hsl(360. * i as f32 / num_shapes as f32, 0.95, 0.7);

        commands.spawn((
            Mesh2d(shape),
            MeshMaterial2d(materials.add(color)),
            Transform::from_xyz(
                // Distribute shapes from -X_EXTENT/2 to +X_EXTENT/2.
                -X_EXTENT / 2. + i as f32 / (num_shapes - 1) as f32 * X_EXTENT,
                Y_EXTENT / 2.,
                0.0,
            ),
        ));
    }

    let rings = [
        meshes.add(Circle::new(50.0).to_ring(THICKNESS)),
        // this visually produces an arc segment but this is not technically accurate
        meshes.add(Ring::new(
            CircularSector::new(50.0, 1.0),
            CircularSector::new(45.0, 1.0),
        )),
        meshes.add(CircularSegment::new(50.0, 1.25).to_ring(THICKNESS)),
        meshes.add({
            // This is an approximation; Ellipse does not implement Inset as concentric ellipses do not have parallel curves
            let outer = Ellipse::new(25.0, 50.0);
            let mut inner = outer;
            inner.half_size -= Vec2::splat(THICKNESS);
            Ring::new(outer, inner)
        }),
        // this is equivalent to the Annulus::new(25.0, 50.0) above
        meshes.add(Ring::new(Circle::new(50.0), Circle::new(25.0))),
        meshes.add(Capsule2d::new(25.0, 50.0).to_ring(THICKNESS)),
        meshes.add(Rhombus::new(75.0, 100.0).to_ring(THICKNESS)),
        meshes.add(Rectangle::new(50.0, 100.0).to_ring(THICKNESS)),
        meshes.add(RegularPolygon::new(50.0, 6).to_ring(THICKNESS)),
        meshes.add(
            Triangle2d::new(
                Vec2::Y * 50.0,
                Vec2::new(-50.0, -50.0),
                Vec2::new(50.0, -50.0),
            )
            .to_ring(THICKNESS),
        ),
    ];
    // Allow for 2 empty spaces
    let num_rings = rings.len() + 2;

    for (i, shape) in rings.into_iter().enumerate() {
        // Distribute colors evenly across the rainbow.
        let color = Color::hsl(360. * i as f32 / num_rings as f32, 0.95, 0.7);

        commands.spawn((
            Mesh2d(shape),
            MeshMaterial2d(materials.add(color)),
            Transform::from_xyz(
                // Distribute shapes from -X_EXTENT/2 to +X_EXTENT/2.
                -X_EXTENT / 2. + i as f32 / (num_rings - 1) as f32 * X_EXTENT,
                -Y_EXTENT / 2.,
                0.0,
            ),
        ));
    }
}
