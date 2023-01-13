import { Fragment } from "react";

export function Scene() {
    return (
        <Fragment>
            <ambientLight/>
            <mesh>
                <boxGeometry attach="geometry" args={[1, 1, 1]}/>
                <meshStandardMaterial attach="material" color="red"/>
            </mesh>
        </Fragment>
    )
}