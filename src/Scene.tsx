import { TransformControls } from "@react-three/drei";
import { Fragment, useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";
import { z } from "zod";

// 4x4 matrix, but all null
export const unsolvedTransformSchema = z.array(z.array(z.nullable(z.number()))).refine(
    (arr) => arr.length === 4 && arr.every((row) => row.length === 4),
    "Must be a 4x4 matrix"
);

// 4x4 matrix, but all numbers
export const solvedTransformSchema = z.array(z.array(z.number())).refine(
    (arr) => arr.length === 4 && arr.every((row) => row.length === 4),
    "Must be a 4x4 matrix"
);

// Either a solved or unsolved transformf
export const transformSchema = z.union([unsolvedTransformSchema, solvedTransformSchema]);

// A map of transforms from one node to another
export const transformMapSchema = z.record(
    z.record(
        z.record(transformSchema)
    )
);

// A map of world transforms
export const worldTransformMapSchema = z.record(
    z.record(
        solvedTransformSchema
    )
);

// A map of edges
export const edgeMapSchema = z.record(
    z.record(
        z.object({
            type: z.union([z.literal(null), z.literal("rigid-known"), z.literal("rigid-unknown"), z.literal("non-rigid-known"), z.literal("non-rigid-unknown")]),
            noise: z.number().nullable(),
        })
    )
);

// The world state
export const worldStateSchema = z.object({
    edges: edgeMapSchema,
    local_transforms: transformMapSchema,
    world_transforms: worldTransformMapSchema
});

// Inferred types
export type WorldState = z.infer<typeof worldStateSchema>;
export type EdgeMap = z.infer<typeof edgeMapSchema>;
export type TransformMap = z.infer<typeof transformMapSchema>;
export type WorldTransformMap = z.infer<typeof worldTransformMapSchema>;
export type Transform = z.infer<typeof transformSchema>;
export type SolvedTransform = z.infer<typeof solvedTransformSchema>;
export type UnsolvedTransform = z.infer<typeof unsolvedTransformSchema>;

const TestComponent = () => {
    console.log("Rendering");
    return null;
}

function transformTransform(transform: Transform, activeFrame: number): Transform {
    // Return the flattened transform of the active frame, but transpose it
    const matrix = transform[activeFrame];
    return [
        [matrix[0][0], matrix[1][0], matrix[2][0], matrix[3][0]],
        [matrix[0][1], matrix[1][1], matrix[2][1], matrix[3][1]],
        [matrix[0][2], matrix[1][2], matrix[2][2], matrix[3][2]],
        [matrix[0][3], matrix[1][3], matrix[2][3], matrix[3][3]],
    ]
}

function TransformVisualizer({transform, activeFrame=0}: {transform: SolvedTransform, activeFrame: number}) {
    const groupRef = useRef<THREE.Group>();
    useEffect(() => {
        console.log("Updating transform, ", transform); 
        // Disable auto updates
        // groupRef.current?.matrixAutoUpdate = false;
        // Set the matrix
        groupRef.current?.matrix.fromArray(transformTransform(transform, activeFrame).flat());
    }, [transform]);
    return (
        <group ref={groupRef} matrixAutoUpdate={false}>
            <TransformControls mode="translate" enabled={false} />
        </group>
    )
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
            // Validate the graph
            console.log(graph);
            worldStateSchema.parse(graph);
            setWorldState(graph as WorldState);
        });
        // Clean up the socket when the component unmounts
        return () => {
            socket.current?.disconnect();
        }
    }, []);

    return (
        <Fragment>
            <ambientLight/>
            {
                worldState && (
                    worldState.world_transforms && (
                        Object.entries(worldState.world_transforms).map(([node, transform]) => (
                            <TransformVisualizer key={node} transform={transform}/>
                        ))
                    )
                )
            }
            <mesh scale={10} rotation={[Math.PI/2,0,0]}>
                <planeGeometry args={[1, 1, 50, 50]}/>
                <meshBasicMaterial wireframe color="black"/>
            </mesh>
        </Fragment>
    )
}