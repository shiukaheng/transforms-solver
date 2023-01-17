import { Fragment, useEffect, useCallback, useRef, useState } from "react";
// Import socket.io-client
import { io, Socket } from "socket.io-client";

type WorldState = {
    edges: EdgeMap;
    local_transforms: TransformMap;
    world_transforms: WorldTransformMap;
}

type EdgeMap = {
    [key: number]: {
        type: null | "rigid-known" | "rigid-unknown" | "non-rigid-known" | "non-rigid-unknown";
        noise: number;
    }
}

type SolvedTransform = [
    [number, number, number, number],
    [number, number, number, number],
    [number, number, number, number],
    [number, number, number, number] // Transform that is solved / known
]

type UnsolvedTransform = [
    [null, null, null, null],
    [null, null, null, null],
    [null, null, null, null],
    [null, null, null, null] // Transform that is unsolved but exists
]

type Transform = SolvedTransform | UnsolvedTransform;

type TransformMap = {
    [key: number]: { // Frame number
        [key: number]: { // Node ID
            [key: number]:  // Neighbor ID
                Transform
        }
    }
}

type WorldTransformMap = {
    [key: number]: { // Frame number
        [key: number]: { // Node ID
            [key: number]:  // Neighbor ID
                SolvedTransform
        }
    }
}
            
export function Scene() {
    // Create a state to hold the world state
    const [worldState, setWorldState] = useState<WorldState>();
    // Maintain a variable that holds the socket
    const socket = useRef<Socket>();
    // Initialize the socket
    useEffect(() => {
        socket.current = io("http://localhost:5000");
        console.log("Socket initialized")
        // Listen for the "graph" event
        socket.current.on("graph", (graph: WorldState) => {
            setWorldState(graph as WorldState);
            console.log(graph);
        });
        // Clean up the socket when the component unmounts
        return () => {
            socket.current?.disconnect();
        }
    }, []);

    return (
        <Fragment>
            <ambientLight/>
            <mesh>
                
            </mesh>
        </Fragment>
    )
}