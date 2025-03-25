import React, { type FC } from 'react';
import {
    EdgeLabelRenderer,
    BaseEdge,
    type EdgeProps,
    type Edge,
    getStraightPath,
} from '@xyflow/react';
import { Tooltip, TooltipTrigger, TooltipContent } from '../../ui/tooltip';
import { interpolateTriColour } from '~/lib/colours';

const EmailEdge: FC<EdgeProps<Edge<{ sentiment: number, emailsSent: number }>>> = ({
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    data,
}) => {
    const [edgePath, labelX, labelY] = getStraightPath({
        sourceX,
        sourceY,
        targetX,
        targetY,
    });

    const stroke = interpolateTriColour(data?.sentiment ?? 0)
    let strokeWidth = 1

    if (data?.emailsSent) {
        strokeWidth = Math.max(Math.log2(data.emailsSent / 2), 1)
    }

    return (
        <>
            <BaseEdge id={id} path={edgePath} style={{ stroke, strokeWidth }} />
            <EdgeLabelRenderer >
                <div
                    style={{
                        transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
                        backgroundColor: stroke
                    }}
                    className={`absolute z-50 p-3 backdrop-blur-lg rounded-lg nodrag nopan pointer-events-auto`}
                >
                    <Tooltip >
                        <TooltipTrigger>
                            <p className='drop-shadow-[0_1.8px_1.8px_rgba(0,0,0,0.8)]'>
                                {data?.sentiment}
                            </p>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Emails Sent between users: {data?.emailsSent}</p>
                            <p>Overall score: {data?.sentiment}</p>
                        </TooltipContent>
                    </Tooltip>
                </div>
            </EdgeLabelRenderer>
        </>
    );
};

export default EmailEdge;
