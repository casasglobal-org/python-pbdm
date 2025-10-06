data = {
  "species_info": {
    "common_name": "Fruit fly",
    "scientific_name": "",
    "species_tag": "fruit_fly"
  },
  "processes": {
    "dynamics": {
      "egg": {
        "scalars": {},
        "rate": {
          "form": "exponential_sat_linear",
          "name": "dev",
          "climate_variable": "temp",
          "parameters": {
            "a": {
              "value": 1
            },
            "b": {
              "value": 0
            },
            "c": {
              "value": 2
            },
            "d": {
              "value": 5
            }
          }
        },
        "del": 42,
        "var": 12
      },
      "larva": {
        "scalars": {},
        "rate": {
          "form": "exponential_sat_linear",
          "name": "dev",
          "climate_variable": "temp",
          "parameters": {
            "a": {
              "value": 1
            },
            "b": {
              "value": 0
            },
            "c": {
              "value": 2
            },
            "d": {
              "value": 5
            }
          }
        },
        "del": 123,
        "var": 2
      },
      "pupa": {
        "scalars": {},
        "rate": {
          "form": "exponential_sat_linear",
          "name": "dev",
          "climate_variable": "temp",
          "parameters": {
            "a": {
              "value": 1
            },
            "b": {
              "value": 0
            },
            "c": {
              "value": 2
            },
            "d": {
              "value": 5
            }
          }
        },
        "del": 534,
        "var": 12
      },
      "adult": {
        "scalars": {},
        "rate": {
          "form": "exponential_sat_linear",
          "name": "dev",
          "climate_variable": "temp",
          "parameters": {
            "a": {
              "value": 1
            },
            "b": {
              "value": 0
            },
            "c": {
              "value": 2
            },
            "d": {
              "value": 5
            }
          }
        },
        "del": 5232,
        "var": 23
      }
    },
    "mortality": {
      "egg": {
        "rates": {
          "mortality_1": {
            "scalars": {},
            "rate": {
              "form": "quadratic",
              "name": "temp",
              "climate_variable": "temp",
              "parameters": {
                "a": {
                  "value": 1
                },
                "b": {
                  "value": 0
                },
                "c": {
                  "value": 0
                }
              }
            }
          }
        }
      },
      "larva": {
        "rates": {
          "mortality_1": {
            "scalars": {},
            "rate": {
              "form": "quadratic",
              "name": "temp",
              "climate_variable": "temp",
              "parameters": {
                "a": {
                  "value": 1
                },
                "b": {
                  "value": 0
                },
                "c": {
                  "value": 0
                }
              }
            }
          },
          "mortality_2": {
            "scalars": {},
            "rate": {
              "form": "linear",
              "name": "dl",
              "climate_variable": "day_length",
              "parameters": {
                "a": {
                  "value": 1
                },
                "b": {
                  "value": 0
                }
              }
            }
          }
        }
      },
      "pupa": {
        "rates": {
          "mortality_1": {
            "scalars": {},
            "rate": {
              "form": "quadratic",
              "name": "temp",
              "climate_variable": "temp",
              "parameters": {
                "a": {
                  "value": 1
                },
                "b": {
                  "value": 0
                },
                "c": {
                  "value": 0
                }
              }
            }
          }
        }
      },
      "adult": {
        "rates": {
          "mortality_1": {
            "scalars": {},
            "rate": {
              "form": "quadratic",
              "name": "temp",
              "climate_variable": "temp",
              "parameters": {
                "a": {
                  "value": 1
                },
                "b": {
                  "value": 0
                },
                "c": {
                  "value": 0
                }
              }
            }
          }
        }
      }
    },
    "reproduction": {
      "adult": {
        "scalars": {
          "scalar_1": {
            "form": "quadratic",
            "name": "temp",
            "climate_variable": "temp",
            "parameters": {
              "a": {
                "value": 1
              },
              "b": {
                "value": 0
              },
              "c": {
                "value": 0
              }
            }
          }
        },
        "rate": {
          "form": "exponential_sat_linear",
          "name": "rep",
          "climate_variable": "temp",
          "parameters": {
            "a": {
              "value": 1
            },
            "b": {
              "value": 0
            },
            "c": {
              "value": 2
            },
            "d": {
              "value": 5
            }
          }
        }
      }
    },
    "interaction": {
      "egg": {},
      "larva": {
        "interaction_1": {
          "scalars": {
            "scalar_1": {
              "form": "quadratic",
              "name": "rh",
              "climate_variable": "rh",
              "parameters": {
                "a": {
                  "value": 1
                },
                "b": {
                  "value": 0
                },
                "c": {
                  "value": 0
                }
              }
            }
          },
          "rate": {
            "form": "quadratic",
            "name": "plant",
            "climate_variable": "temp",
            "parameters": {
              "a": {
                "value": 1
              },
              "b": {
                "value": 0
              },
              "c": {
                "value": 0
              }
            }
          }
        }
      },
      "pupa": {},
      "adult": {}
    }
  },
  "stages": {
    "egg": {
      "label": "Egg",
      "plural": "Eggs",
      "reproductive": False
    },
    "larva": {
      "label": "Larva",
      "plural": "Larvae",
      "reproductive": False
    },
    "pupa": {
      "label": "Pupa",
      "plural": "Pupae",
      "reproductive": False
    },
    "adult": {
      "label": "Adult",
      "plural": "Adults",
      "reproductive": True
    }
  }
}