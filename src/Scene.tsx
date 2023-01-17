import { Fragment, useEffect, useCallback, useRef, useState } from "react";
// Import socket.io-client
import { io, Socket } from "socket.io-client";

type WorldState = {
    edges: EdgeMap;
    local_transforms: TransformMap;
    world_transforms: WorldTransformMap;
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
            // setWorldState(graph);
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