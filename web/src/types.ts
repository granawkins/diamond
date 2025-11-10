type State = {
    legs: {
        [key: string]: {
            [key: string]: number
        }
    }
    battery: {
        percentage: number
        status: string
    }
}

export type { State }