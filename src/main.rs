mod config;

use bevy::prelude::*;
fn main() {
    let mut app = App::new();
    app.add_plugins(DefaultPlugins)
        .add_systems(Startup, config::create_scenario)
        .run();
}
